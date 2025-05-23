import { useState, useRef } from 'react';
import { crmApi } from '@/services/crm/crmApi';
import { Product } from '@/types/crm';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/components/ui/use-toast';
import { UploadIcon, XIcon, ImageIcon, ArrowUpIcon, ArrowDownIcon } from 'lucide-react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { restrictToVerticalAxis } from '@dnd-kit/modifiers';

interface ProductImageUploadProps {
  product: Product;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface SortableImageProps {
  id: string;
  src: string;
  name: string;
  onDelete: (id: string) => void;
}

function SortableImage({ id, src, name, onDelete }: SortableImageProps) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });
  
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };
  
  return (
    <div 
      ref={setNodeRef} 
      style={style} 
      className="flex items-center gap-3 p-2 border rounded-md bg-background"
      {...attributes}
      {...listeners}
    >
      <div className="flex-shrink-0 w-16 h-16 relative">
        <img 
          src={src} 
          alt={name} 
          className="w-full h-full object-cover rounded-md"
        />
      </div>
      <div className="flex-grow">
        <p className="text-sm font-medium truncate">{name}</p>
        <p className="text-xs text-muted-foreground">Drag to reorder</p>
      </div>
      <Button 
        variant="ghost" 
        size="icon" 
        className="flex-shrink-0"
        onClick={() => onDelete(id)}
      >
        <XIcon className="h-4 w-4" />
      </Button>
    </div>
  );
}

export default function ProductImageUpload({ product, isOpen, onClose, onSuccess }: ProductImageUploadProps) {
  const { toast } = useToast();
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isPrimary, setIsPrimary] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [images, setImages] = useState<any[]>(product.images || []);
  
  // API hooks
  const [uploadProductImage] = crmApi.useUploadProductImageMutation();
  const [deleteProductImage] = crmApi.useDeleteProductImageMutation();
  const [reorderProductImages] = crmApi.useReorderProductImagesMutation();
  
  // DnD sensors
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );
  
  // Handle file selection
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      await handleUpload(file);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };
  
  // Handle file upload button click
  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };
  
  // Handle upload
  const handleUpload = async (file: File) => {
    setIsUploading(true);
    
    try {
      await uploadProductImage({
        product_id: product.id,
        image: file,
        is_primary: isPrimary,
      }).unwrap();
      
      toast({
        title: 'Image Uploaded',
        description: 'Product image has been uploaded successfully.',
      });
      
      onSuccess();
    } catch (error) {
      console.error('Error uploading image:', error);
      toast({
        title: 'Upload Failed',
        description: 'An error occurred while uploading the image.',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };
  
  // Handle image deletion
  const handleDeleteImage = async (imageId: string) => {
    try {
      await deleteProductImage({
        product_id: product.id,
        image_id: imageId,
      }).unwrap();
      
      // Update local state
      setImages(images.filter(img => img.id !== imageId));
      
      toast({
        title: 'Image Deleted',
        description: 'Product image has been deleted successfully.',
      });
      
      onSuccess();
    } catch (error) {
      console.error('Error deleting image:', error);
      toast({
        title: 'Delete Failed',
        description: 'An error occurred while deleting the image.',
        variant: 'destructive',
      });
    }
  };
  
  // Handle drag end
  const handleDragEnd = async (event: any) => {
    const { active, over } = event;
    
    if (active.id !== over.id) {
      // Find the indices
      const oldIndex = images.findIndex(img => img.id === active.id);
      const newIndex = images.findIndex(img => img.id === over.id);
      
      // Reorder locally
      const newImages = [...images];
      const [movedItem] = newImages.splice(oldIndex, 1);
      newImages.splice(newIndex, 0, movedItem);
      
      // Update local state
      setImages(newImages);
      
      // Update on server
      try {
        await reorderProductImages({
          product_id: product.id,
          image_ids: newImages.map(img => img.id),
        }).unwrap();
        
        toast({
          title: 'Images Reordered',
          description: 'Product images have been reordered successfully.',
        });
        
        onSuccess();
      } catch (error) {
        console.error('Error reordering images:', error);
        toast({
          title: 'Reorder Failed',
          description: 'An error occurred while reordering the images.',
          variant: 'destructive',
        });
        
        // Revert to original order
        setImages(product.images || []);
      }
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Product Images</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Upload New Image</Label>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <div 
              className="border-2 border-dashed rounded-md p-6 text-center cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={handleUploadClick}
            >
              <div className="flex flex-col items-center justify-center gap-2">
                <UploadIcon className="h-8 w-8 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Click to select an image
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 mt-2">
              <Switch
                id="primary-image"
                checked={isPrimary}
                onCheckedChange={setIsPrimary}
              />
              <Label htmlFor="primary-image">Set as primary image</Label>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label>Current Images</Label>
            {images && images.length > 0 ? (
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={handleDragEnd}
                modifiers={[restrictToVerticalAxis]}
              >
                <SortableContext
                  items={images.map(img => img.id)}
                  strategy={verticalListSortingStrategy}
                >
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {images.map((image) => (
                      <SortableImage
                        key={image.id}
                        id={image.id}
                        src={image.src}
                        name={image.name || 'Product Image'}
                        onDelete={handleDeleteImage}
                      />
                    ))}
                  </div>
                </SortableContext>
              </DndContext>
            ) : (
              <div className="text-center py-4 border rounded-md">
                <ImageIcon className="h-8 w-8 mx-auto text-muted-foreground" />
                <p className="text-sm text-muted-foreground mt-2">No images yet</p>
              </div>
            )}
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
