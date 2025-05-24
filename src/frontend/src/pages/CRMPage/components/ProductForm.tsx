import { useState, useEffect } from 'react';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { crmApi } from '@/services/crm/crmApi';
import { Product, ProductCreate, ProductUpdate } from '@/types/crm';
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
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent } from '@/components/ui/card';
import { ImageIcon, PlusIcon, MessageSquareIcon, StarIcon } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import ProductImageUpload from './ProductImageUpload';
import ProductReviews from './ProductReviews';

// Form schema
const productFormSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  slug: z.string().min(1, 'Slug is required'),
  description: z.string().optional(),
  short_description: z.string().optional(),
  sku: z.string().optional(),
  price: z.coerce.number().min(0, 'Price must be a positive number'),
  regular_price: z.coerce.number().min(0, 'Regular price must be a positive number'),
  sale_price: z.coerce.number().min(0, 'Sale price must be a positive number').optional(),
  on_sale: z.boolean().default(false),
  status: z.string().default('draft'),
  featured: z.boolean().default(false),
  catalog_visibility: z.string().default('visible'),
  tax_status: z.string().default('taxable'),
  tax_class: z.string().optional(),
  manage_stock: z.boolean().default(false),
  stock_quantity: z.coerce.number().optional(),
  stock_status: z.string().default('instock'),
  backorders: z.string().default('no'),
  backorders_allowed: z.boolean().default(false),
  backordered: z.boolean().default(false),
  weight: z.string().optional(),
  virtual: z.boolean().default(false),
  downloadable: z.boolean().default(false),
  sold_individually: z.boolean().default(false),
  external_url: z.string().optional(),
  button_text: z.string().optional(),
  menu_order: z.coerce.number().default(0),
  purchasable: z.boolean().default(true),
});

type ProductFormValues = z.infer<typeof productFormSchema>;

interface ProductFormProps {
  workspaceId: string;
  product?: Product | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ProductForm({ workspaceId, product, onClose, onSuccess }: ProductFormProps) {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('general');
  const [showImageUpload, setShowImageUpload] = useState(false);
  const [showReviews, setShowReviews] = useState(false);

  // API hooks
  const [createProduct, { isLoading: isCreating }] = crmApi.useCreateProductMutation();
  const [updateProduct, { isLoading: isUpdating }] = crmApi.useUpdateProductMutation();
  const { data: categories } = crmApi.useGetProductCategoriesQuery({ workspace_id: workspaceId });
  const { data: attributes } = crmApi.useGetProductAttributesQuery({ workspace_id: workspaceId });

  // Handle image upload
  const handleImageUpload = () => {
    if (product) {
      setShowImageUpload(true);
    } else {
      toast({
        title: "Save Product First",
        description: "Please save the product before adding images.",
        variant: "default",
      });
    }
  };

  const handleImageUploadClose = () => {
    setShowImageUpload(false);
  };

  const handleImageUploadSuccess = () => {
    // Refresh product data
    if (product) {
      crmApi.useGetProductQuery(product.id).refetch();
    }
  };

  // Handle reviews dialog
  const handleReviews = () => {
    if (product) {
      setShowReviews(true);
    } else {
      toast({
        title: "Save Product First",
        description: "Please save the product before managing reviews.",
        variant: "default",
      });
    }
  };

  const handleReviewsClose = () => {
    setShowReviews(false);
  };

  // Form setup
  const form = useForm<ProductFormValues>({
    resolver: zodResolver(productFormSchema),
    defaultValues: {
      name: '',
      slug: '',
      description: '',
      short_description: '',
      sku: '',
      price: 0,
      regular_price: 0,
      sale_price: undefined,
      on_sale: false,
      status: 'draft',
      featured: false,
      catalog_visibility: 'visible',
      tax_status: 'taxable',
      tax_class: '',
      manage_stock: false,
      stock_quantity: undefined,
      stock_status: 'instock',
      backorders: 'no',
      backorders_allowed: false,
      backordered: false,
      weight: '',
      virtual: false,
      downloadable: false,
      sold_individually: false,
      external_url: '',
      button_text: '',
      menu_order: 0,
      purchasable: true,
    },
  });

  // Populate form with product data if editing
  useEffect(() => {
    if (product) {
      form.reset({
        name: product.name,
        slug: product.slug,
        description: product.description || '',
        short_description: product.short_description || '',
        sku: product.sku || '',
        price: product.price,
        regular_price: product.regular_price,
        sale_price: product.sale_price,
        on_sale: product.on_sale,
        status: product.status,
        featured: product.featured,
        catalog_visibility: product.catalog_visibility,
        tax_status: product.tax_status,
        tax_class: product.tax_class || '',
        manage_stock: product.manage_stock,
        stock_quantity: product.stock_quantity,
        stock_status: product.stock_status,
        backorders: product.backorders,
        backorders_allowed: product.backorders_allowed,
        backordered: product.backordered,
        weight: product.weight || '',
        virtual: product.virtual,
        downloadable: product.downloadable,
        sold_individually: product.sold_individually,
        external_url: product.external_url || '',
        button_text: product.button_text || '',
        menu_order: product.menu_order,
        purchasable: product.purchasable,
      });
    }
  }, [product, form]);

  // Handle form submission
  const onSubmit = async (values: ProductFormValues) => {
    try {
      if (product) {
        // Update existing product
        await updateProduct({
          id: product.id,
          product: values as ProductUpdate,
        }).unwrap();
      } else {
        // Create new product
        await createProduct({
          ...values,
          workspace_id: workspaceId,
        } as ProductCreate).unwrap();
      }
      onSuccess();
    } catch (error) {
      console.error('Error saving product:', error);
      toast({
        title: 'Error',
        description: 'Failed to save product. Please try again.',
        variant: 'destructive',
      });
    }
  };

  // Generate slug from name
  const generateSlug = () => {
    const name = form.getValues('name');
    if (name) {
      const slug = name
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/(^-|-$)/g, '');
      form.setValue('slug', slug);
    }
  };

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{product ? 'Edit Product' : 'Create Product'}</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid grid-cols-6 mb-4">
                <TabsTrigger value="general">General</TabsTrigger>
                <TabsTrigger value="inventory">Inventory</TabsTrigger>
                <TabsTrigger value="shipping">Shipping</TabsTrigger>
                <TabsTrigger value="advanced">Advanced</TabsTrigger>
                <TabsTrigger value="images">Images</TabsTrigger>
                <TabsTrigger value="reviews">Reviews</TabsTrigger>
              </TabsList>

              <TabsContent value="general" className="space-y-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Product Name*</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          placeholder="Enter product name"
                          onBlur={() => {
                            if (!form.getValues('slug')) {
                              generateSlug();
                            }
                          }}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="flex gap-4">
                  <FormField
                    control={form.control}
                    name="slug"
                    render={({ field }) => (
                      <FormItem className="flex-1">
                        <FormLabel>Slug*</FormLabel>
                        <div className="flex gap-2">
                          <FormControl>
                            <Input {...field} placeholder="product-slug" />
                          </FormControl>
                          <Button
                            type="button"
                            variant="outline"
                            onClick={generateSlug}
                            className="shrink-0"
                          >
                            Generate
                          </Button>
                        </div>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="sku"
                    render={({ field }) => (
                      <FormItem className="flex-1">
                        <FormLabel>SKU</FormLabel>
                        <FormControl>
                          <Input {...field} placeholder="SKU" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="short_description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Short Description</FormLabel>
                      <FormControl>
                        <Textarea
                          {...field}
                          placeholder="Brief description of the product"
                          rows={2}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Full Description</FormLabel>
                      <FormControl>
                        <Textarea
                          {...field}
                          placeholder="Detailed description of the product"
                          rows={5}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="regular_price"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Regular Price*</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            type="number"
                            min="0"
                            step="0.01"
                            placeholder="0.00"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="sale_price"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Sale Price</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            type="number"
                            min="0"
                            step="0.01"
                            placeholder="0.00"
                            value={field.value || ''}
                            onChange={(e) => {
                              field.onChange(e.target.value ? Number(e.target.value) : undefined);
                              if (e.target.value && Number(e.target.value) > 0) {
                                form.setValue('on_sale', true);
                              } else {
                                form.setValue('on_sale', false);
                              }
                            }}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="status"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Status</FormLabel>
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
                            <SelectItem value="draft">Draft</SelectItem>
                            <SelectItem value="pending">Pending</SelectItem>
                            <SelectItem value="publish">Published</SelectItem>
                            <SelectItem value="private">Private</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="featured"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                        <div className="space-y-0.5">
                          <FormLabel>Featured Product</FormLabel>
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
                </div>
              </TabsContent>

              <TabsContent value="inventory" className="space-y-4">
                <FormField
                  control={form.control}
                  name="manage_stock"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                      <div className="space-y-0.5">
                        <FormLabel>Manage Stock</FormLabel>
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

                {form.watch('manage_stock') && (
                  <FormField
                    control={form.control}
                    name="stock_quantity"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Stock Quantity</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            type="number"
                            min="0"
                            step="1"
                            placeholder="0"
                            value={field.value === undefined ? '' : field.value}
                            onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : undefined)}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                )}

                <FormField
                  control={form.control}
                  name="stock_status"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Stock Status</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                        value={field.value}
                        disabled={form.watch('manage_stock')}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select stock status" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="instock">In Stock</SelectItem>
                          <SelectItem value="outofstock">Out of Stock</SelectItem>
                          <SelectItem value="onbackorder">On Backorder</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="backorders"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Backorders</FormLabel>
                      <Select
                        onValueChange={(value) => {
                          field.onChange(value);
                          form.setValue('backorders_allowed', value !== 'no');
                        }}
                        defaultValue={field.value}
                        value={field.value}
                        disabled={!form.watch('manage_stock')}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select backorder option" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="no">Do not allow</SelectItem>
                          <SelectItem value="notify">Allow, but notify customer</SelectItem>
                          <SelectItem value="yes">Allow</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="sold_individually"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                      <div className="space-y-0.5">
                        <FormLabel>Sold Individually</FormLabel>
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
              </TabsContent>

              <TabsContent value="shipping" className="space-y-4">
                <FormField
                  control={form.control}
                  name="weight"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Weight</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="0" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="virtual"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                      <div className="space-y-0.5">
                        <FormLabel>Virtual Product</FormLabel>
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

                <FormField
                  control={form.control}
                  name="downloadable"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                      <div className="space-y-0.5">
                        <FormLabel>Downloadable Product</FormLabel>
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
              </TabsContent>

              <TabsContent value="advanced" className="space-y-4">
                <FormField
                  control={form.control}
                  name="catalog_visibility"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Catalog Visibility</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                        value={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select visibility" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="visible">Visible</SelectItem>
                          <SelectItem value="catalog">Catalog only</SelectItem>
                          <SelectItem value="search">Search only</SelectItem>
                          <SelectItem value="hidden">Hidden</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="tax_status"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tax Status</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                        value={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select tax status" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="taxable">Taxable</SelectItem>
                          <SelectItem value="shipping">Shipping only</SelectItem>
                          <SelectItem value="none">None</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="tax_class"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tax Class</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="Standard" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="menu_order"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Menu Order</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type="number"
                          min="0"
                          step="1"
                          placeholder="0"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="purchasable"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                      <div className="space-y-0.5">
                        <FormLabel>Purchasable</FormLabel>
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
              </TabsContent>

              <TabsContent value="images" className="space-y-4">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Product Images</h3>
                    <Button type="button" variant="outline" onClick={handleImageUpload}>
                      <PlusIcon className="h-4 w-4 mr-2" />
                      Manage Images
                    </Button>
                  </div>

                  {product && product.images && product.images.length > 0 ? (
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {product.images.map((image) => (
                        <Card key={image.id} className="overflow-hidden">
                          <CardContent className="p-0">
                            <img
                              src={image.src}
                              alt={image.name || 'Product image'}
                              className="w-full h-32 object-cover"
                            />
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 border rounded-md">
                      <ImageIcon className="h-10 w-10 mx-auto text-muted-foreground" />
                      <p className="mt-2 text-sm text-muted-foreground">
                        No images yet. Click "Manage Images" to add product images.
                      </p>
                    </div>
                  )}

                  <p className="text-sm text-muted-foreground mt-4">
                    Note: You need to save the product before you can add images.
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="reviews" className="space-y-4">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Product Reviews</h3>
                    <Button type="button" variant="outline" onClick={handleReviews}>
                      <MessageSquareIcon className="h-4 w-4 mr-2" />
                      Manage Reviews
                    </Button>
                  </div>

                  {product && product.reviews && product.reviews.length > 0 ? (
                    <div className="space-y-4">
                      <div className="flex items-center gap-2">
                        <div className="flex">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <StarIcon
                              key={star}
                              className={`h-5 w-5 ${
                                star <= Math.round(
                                  product.reviews.reduce((sum, review) => sum + review.rating, 0) / product.reviews.length
                                )
                                  ? 'text-yellow-400 fill-yellow-400'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        <span className="text-sm font-medium">
                          {product.reviews.length} {product.reviews.length === 1 ? 'review' : 'reviews'}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {product.reviews
                          .filter(review => review.status === 'approved')
                          .slice(0, 4)
                          .map((review) => (
                            <Card key={review.id} className="overflow-hidden">
                              <CardContent className="p-4">
                                <div className="flex items-center gap-2 mb-2">
                                  {[1, 2, 3, 4, 5].map((star) => (
                                    <StarIcon
                                      key={star}
                                      className={`h-4 w-4 ${
                                        star <= review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'
                                      }`}
                                    />
                                  ))}
                                </div>
                                {review.title && (
                                  <p className="font-medium text-sm mb-1">{review.title}</p>
                                )}
                                {review.content && (
                                  <p className="text-sm text-muted-foreground line-clamp-3">{review.content}</p>
                                )}
                                <p className="text-xs mt-2">by {review.reviewer_name}</p>
                              </CardContent>
                            </Card>
                          ))}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 border rounded-md">
                      <MessageSquareIcon className="h-10 w-10 mx-auto text-muted-foreground" />
                      <p className="mt-2 text-sm text-muted-foreground">
                        No reviews yet. Click "Manage Reviews" to add product reviews.
                      </p>
                    </div>
                  )}

                  <p className="text-sm text-muted-foreground mt-4">
                    Note: You need to save the product before you can manage reviews.
                  </p>
                </div>
              </TabsContent>
            </Tabs>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={isCreating || isUpdating}>
                {isCreating || isUpdating ? 'Saving...' : product ? 'Update Product' : 'Create Product'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>

      {product && showImageUpload && (
        <ProductImageUpload
          product={product}
          isOpen={showImageUpload}
          onClose={handleImageUploadClose}
          onSuccess={handleImageUploadSuccess}
        />
      )}

      {product && showReviews && (
        <ProductReviews
          product={product}
          isOpen={showReviews}
          onClose={handleReviewsClose}
          isAdmin={true}
        />
      )}
    </Dialog>
  );
}
