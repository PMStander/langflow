import { useState } from 'react';
import { crmApi } from '@/services/crm/crmApi';
import { Product, ProductReview, ProductReviewCreate } from '@/types/crm';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Star, StarIcon, Edit2Icon, Trash2Icon, CheckCircleIcon } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface ProductReviewsProps {
  product: Product;
  isOpen: boolean;
  onClose: () => void;
  isAdmin?: boolean;
}

// Form schema for creating a review
const reviewFormSchema = z.object({
  rating: z.number().min(1).max(5),
  title: z.string().optional(),
  content: z.string().optional(),
  reviewer_name: z.string().min(1, 'Name is required'),
  reviewer_email: z.string().email('Invalid email address').optional().or(z.literal('')),
  verified_purchase: z.boolean().default(false),
});

// Form schema for updating a review (admin only)
const adminReviewFormSchema = reviewFormSchema.extend({
  status: z.string(),
});

type ReviewFormValues = z.infer<typeof reviewFormSchema>;
type AdminReviewFormValues = z.infer<typeof adminReviewFormSchema>;

export default function ProductReviews({ product, isOpen, onClose, isAdmin = false }: ProductReviewsProps) {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<'list' | 'create' | 'edit'>('list');
  const [selectedReview, setSelectedReview] = useState<ProductReview | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  
  // API hooks
  const { data: reviews, isLoading, refetch } = crmApi.useGetProductReviewsQuery({
    product_id: product.id,
    status: isAdmin ? undefined : 'approved',
  });
  const [createReview] = crmApi.useCreateProductReviewMutation();
  const [updateReview] = crmApi.useUpdateProductReviewMutation();
  const [deleteReview] = crmApi.useDeleteProductReviewMutation();
  
  // Form for creating a review
  const form = useForm<ReviewFormValues>({
    resolver: zodResolver(reviewFormSchema),
    defaultValues: {
      rating: 5,
      title: '',
      content: '',
      reviewer_name: '',
      reviewer_email: '',
      verified_purchase: false,
    },
  });
  
  // Form for admin editing a review
  const adminForm = useForm<AdminReviewFormValues>({
    resolver: zodResolver(adminReviewFormSchema),
    defaultValues: {
      rating: 5,
      title: '',
      content: '',
      reviewer_name: '',
      reviewer_email: '',
      verified_purchase: false,
      status: 'pending',
    },
  });
  
  // Handle creating a new review
  const handleCreateReview = async (values: ReviewFormValues) => {
    try {
      await createReview({
        ...values,
        product_id: product.id,
      }).unwrap();
      
      toast({
        title: 'Review Submitted',
        description: 'Your review has been submitted successfully and is pending approval.',
      });
      
      setActiveTab('list');
      refetch();
    } catch (error) {
      console.error('Error creating review:', error);
      toast({
        title: 'Error',
        description: 'Failed to submit review. Please try again.',
        variant: 'destructive',
      });
    }
  };
  
  // Handle updating a review (admin only)
  const handleUpdateReview = async (values: AdminReviewFormValues) => {
    if (!selectedReview) return;
    
    try {
      await updateReview({
        id: selectedReview.id,
        review: values,
      }).unwrap();
      
      toast({
        title: 'Review Updated',
        description: 'The review has been updated successfully.',
      });
      
      setActiveTab('list');
      setSelectedReview(null);
      refetch();
    } catch (error) {
      console.error('Error updating review:', error);
      toast({
        title: 'Error',
        description: 'Failed to update review. Please try again.',
        variant: 'destructive',
      });
    }
  };
  
  // Handle deleting a review (admin only)
  const handleDeleteReview = async () => {
    if (!selectedReview) return;
    
    try {
      await deleteReview(selectedReview.id).unwrap();
      
      toast({
        title: 'Review Deleted',
        description: 'The review has been deleted successfully.',
      });
      
      setShowDeleteConfirm(false);
      setSelectedReview(null);
      refetch();
    } catch (error) {
      console.error('Error deleting review:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete review. Please try again.',
        variant: 'destructive',
      });
    }
  };
  
  // Handle edit button click (admin only)
  const handleEditClick = (review: ProductReview) => {
    setSelectedReview(review);
    adminForm.reset({
      rating: review.rating,
      title: review.title || '',
      content: review.content || '',
      reviewer_name: review.reviewer_name || '',
      reviewer_email: review.reviewer_email || '',
      verified_purchase: review.verified_purchase,
      status: review.status,
    });
    setActiveTab('edit');
  };
  
  // Handle delete button click (admin only)
  const handleDeleteClick = (review: ProductReview) => {
    setSelectedReview(review);
    setShowDeleteConfirm(true);
  };
  
  // Render star rating
  const renderStarRating = (rating: number) => {
    return (
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => (
          <StarIcon
            key={star}
            className={`h-5 w-5 ${
              star <= rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };
  
  // Get status badge color
  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-500';
      case 'pending':
        return 'bg-yellow-500';
      case 'rejected':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Product Reviews</DialogTitle>
        </DialogHeader>
        
        {activeTab === 'list' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">
                Reviews for {product.name}
              </h3>
              <Button onClick={() => {
                form.reset();
                setActiveTab('create');
              }}>
                Write a Review
              </Button>
            </div>
            
            {isLoading ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground">Loading reviews...</p>
              </div>
            ) : reviews && reviews.length > 0 ? (
              <div className="space-y-4">
                {reviews.map((review) => (
                  <Card key={review.id}>
                    <CardHeader className="pb-2">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-base">{review.title || 'Review'}</CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            {renderStarRating(review.rating)}
                            <span className="text-sm text-muted-foreground">
                              by {review.reviewer_name}
                            </span>
                          </div>
                        </div>
                        {isAdmin && (
                          <div className="flex items-center gap-2">
                            <Badge className={getStatusBadgeColor(review.status)}>
                              {review.status}
                            </Badge>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleEditClick(review)}
                            >
                              <Edit2Icon className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeleteClick(review)}
                            >
                              <Trash2Icon className="h-4 w-4" />
                            </Button>
                          </div>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent>
                      {review.content && (
                        <p className="text-sm">{review.content}</p>
                      )}
                    </CardContent>
                    {review.verified_purchase && (
                      <CardFooter className="pt-0">
                        <div className="flex items-center text-green-600 text-xs">
                          <CheckCircleIcon className="h-3 w-3 mr-1" />
                          Verified Purchase
                        </div>
                      </CardFooter>
                    )}
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 border rounded-md">
                <p className="text-muted-foreground">No reviews yet</p>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'create' && (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleCreateReview)} className="space-y-4">
              <FormField
                control={form.control}
                name="rating"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Rating*</FormLabel>
                    <div className="flex gap-2">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`h-8 w-8 cursor-pointer ${
                            star <= field.value ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'
                          }`}
                          onClick={() => field.onChange(star)}
                        />
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Review Title</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="Summarize your review" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="content"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Review Content</FormLabel>
                    <FormControl>
                      <Textarea
                        {...field}
                        placeholder="Write your review here"
                        rows={4}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="reviewer_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Your Name*</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="Enter your name" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="reviewer_email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Your Email</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="Enter your email" type="email" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="verified_purchase"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                    <div className="space-y-0.5">
                      <FormLabel>Verified Purchase</FormLabel>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
              
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setActiveTab('list')}>
                  Cancel
                </Button>
                <Button type="submit">
                  Submit Review
                </Button>
              </DialogFooter>
            </form>
          </Form>
        )}
        
        {activeTab === 'edit' && isAdmin && selectedReview && (
          <Form {...adminForm}>
            <form onSubmit={adminForm.handleSubmit(handleUpdateReview)} className="space-y-4">
              <FormField
                control={adminForm.control}
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Review Status*</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      value={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="approved">Approved</SelectItem>
                        <SelectItem value="rejected">Rejected</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={adminForm.control}
                name="rating"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Rating*</FormLabel>
                    <div className="flex gap-2">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`h-8 w-8 cursor-pointer ${
                            star <= field.value ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'
                          }`}
                          onClick={() => field.onChange(star)}
                        />
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={adminForm.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Review Title</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="Summarize your review" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={adminForm.control}
                name="content"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Review Content</FormLabel>
                    <FormControl>
                      <Textarea
                        {...field}
                        placeholder="Write your review here"
                        rows={4}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={adminForm.control}
                name="reviewer_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Reviewer Name*</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="Enter reviewer name" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={adminForm.control}
                name="reviewer_email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Reviewer Email</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="Enter reviewer email" type="email" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={adminForm.control}
                name="verified_purchase"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                    <div className="space-y-0.5">
                      <FormLabel>Verified Purchase</FormLabel>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
              
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setActiveTab('list')}>
                  Cancel
                </Button>
                <Button type="submit">
                  Update Review
                </Button>
              </DialogFooter>
            </form>
          </Form>
        )}
        
        {activeTab === 'list' && (
          <DialogFooter>
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
      
      <AlertDialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Review</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this review? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteReview}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Dialog>
  );
}
