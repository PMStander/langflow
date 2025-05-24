import { useState } from 'react';
import { useWorkspaceStore } from '@/stores/workspaceStore';
import { useGetProductsQuery } from '@/controllers/API/queries/crm';
import { Product, ProductStatus } from '@/types/crm';
import { extractItems } from '@/types/crm/pagination';
import CRMSidebarComponent from '@/components/core/crmSidebarComponent';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PlusIcon, SearchIcon, FilterIcon, UploadIcon, DownloadIcon, ShoppingCartIcon } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { formatCurrency } from '@/lib/utils';
import { useToast } from '@/components/ui/use-toast';
import ProductForm from './components/ProductForm';
import ProductImportExport from './components/ProductImportExport';
import EcommerceIntegration from './components/EcommerceIntegration';

export default function ProductsPage() {
  const { toast } = useToast();
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);
  const [activeTab, setActiveTab] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showCreateForm, setShowCreateForm] = useState<boolean>(false);
  const [showImportExport, setShowImportExport] = useState<boolean>(false);
  const [showEcommerceIntegration, setShowEcommerceIntegration] = useState<boolean>(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  // API hooks
  const { data: productsResponse, isLoading, refetch } = useGetProductsQuery({
    workspace_id: currentWorkspaceId || '',
    status: activeTab !== 'all' ? activeTab : undefined,
  });

  // Extract products from response (handle both paginated and non-paginated)
  const products = productsResponse ? extractItems(productsResponse) : [];

  // Filter products based on search query
  const filteredProducts = products?.filter((product) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      product.name.toLowerCase().includes(query) ||
      product.sku?.toLowerCase().includes(query) ||
      product.description?.toLowerCase().includes(query)
    );
  });

  // Handle tab change
  const handleTabChange = (value: string) => {
    setActiveTab(value);
  };

  // Handle product creation
  const handleCreateProduct = () => {
    setSelectedProduct(null);
    setShowCreateForm(true);
  };

  // Handle product edit
  const handleEditProduct = (product: Product) => {
    setSelectedProduct(product);
    setShowCreateForm(true);
  };

  // Handle form close
  const handleFormClose = () => {
    setShowCreateForm(false);
    setSelectedProduct(null);
  };

  // Handle import/export dialog
  const handleImportExport = () => {
    setShowImportExport(true);
  };

  const handleImportExportClose = () => {
    setShowImportExport(false);
  };

  // Handle e-commerce integration dialog
  const handleEcommerceIntegration = () => {
    setShowEcommerceIntegration(true);
  };

  const handleEcommerceIntegrationClose = () => {
    setShowEcommerceIntegration(false);
  };

  // Handle form submit success
  const handleFormSuccess = () => {
    setShowCreateForm(false);
    setSelectedProduct(null);
    refetch();
    toast({
      title: 'Success',
      description: selectedProduct ? 'Product updated successfully' : 'Product created successfully',
    });
  };

  // Get status badge color
  const getStatusBadgeColor = (status: ProductStatus) => {
    switch (status) {
      case 'publish':
        return 'bg-green-500';
      case 'draft':
        return 'bg-gray-500';
      case 'pending':
        return 'bg-yellow-500';
      case 'private':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="flex h-full">
      <CRMSidebarComponent />
      <div className="flex-1 overflow-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Products</h1>
            <p className="text-muted-foreground">
              Manage your products and inventory
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleImportExport}>
              <UploadIcon className="mr-2 h-4 w-4" />
              Import/Export
            </Button>
            <Button variant="outline" onClick={handleEcommerceIntegration}>
              <ShoppingCartIcon className="mr-2 h-4 w-4" />
              E-commerce
            </Button>
            <Button onClick={handleCreateProduct}>
              <PlusIcon className="mr-2 h-4 w-4" />
              Add Product
            </Button>
          </div>
        </div>

      <Tabs defaultValue="all" value={activeTab} onValueChange={handleTabChange} className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="publish">Published</TabsTrigger>
            <TabsTrigger value="draft">Draft</TabsTrigger>
            <TabsTrigger value="pending">Pending</TabsTrigger>
            <TabsTrigger value="private">Private</TabsTrigger>
          </TabsList>
          <div className="flex items-center space-x-2">
            <div className="relative">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search products..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select defaultValue="name">
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="name">Name</SelectItem>
                <SelectItem value="price">Price</SelectItem>
                <SelectItem value="created_at">Date Created</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <TabsContent value="all" className="mt-0">
          {renderProductList(filteredProducts, isLoading, handleEditProduct)}
        </TabsContent>
        <TabsContent value="publish" className="mt-0">
          {renderProductList(filteredProducts, isLoading, handleEditProduct)}
        </TabsContent>
        <TabsContent value="draft" className="mt-0">
          {renderProductList(filteredProducts, isLoading, handleEditProduct)}
        </TabsContent>
        <TabsContent value="pending" className="mt-0">
          {renderProductList(filteredProducts, isLoading, handleEditProduct)}
        </TabsContent>
        <TabsContent value="private" className="mt-0">
          {renderProductList(filteredProducts, isLoading, handleEditProduct)}
        </TabsContent>
      </Tabs>

      {showCreateForm && (
        <ProductForm
          workspaceId={currentWorkspaceId || ''}
          product={selectedProduct}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}

      {showImportExport && (
        <ProductImportExport
          isOpen={showImportExport}
          onClose={handleImportExportClose}
        />
      )}

      {showEcommerceIntegration && (
        <EcommerceIntegration
          isOpen={showEcommerceIntegration}
          onClose={handleEcommerceIntegrationClose}
          onSuccess={() => refetch()}
        />
      )}
      </div>
    </div>
  );
}

// Helper function to render product list
function renderProductList(
  products: Product[] | undefined,
  isLoading: boolean,
  onEdit: (product: Product) => void
) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i} className="cursor-pointer hover:shadow-md transition-shadow">
            <CardHeader className="pb-2">
              <Skeleton className="h-6 w-3/4 mb-2" />
              <Skeleton className="h-4 w-1/4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-4 w-full mb-2" />
              <Skeleton className="h-4 w-2/3" />
              <div className="flex justify-between items-center mt-4">
                <Skeleton className="h-6 w-1/3" />
                <Skeleton className="h-6 w-1/4" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">No products found</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {products.map((product) => (
        <Card
          key={product.id}
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => onEdit(product)}
        >
          <CardHeader className="pb-2">
            <div className="flex justify-between items-start">
              <CardTitle className="text-lg">{product.name}</CardTitle>
              <Badge className={getStatusBadgeColor(product.status as ProductStatus)}>
                {product.status}
              </Badge>
            </div>
            {product.sku && <p className="text-sm text-muted-foreground">SKU: {product.sku}</p>}
          </CardHeader>
          <CardContent>
            {product.short_description && (
              <p className="text-sm text-muted-foreground mb-2 line-clamp-2">{product.short_description}</p>
            )}
            <div className="flex justify-between items-center mt-4">
              <div>
                <p className="font-bold text-lg">{formatCurrency(product.price)}</p>
                {product.on_sale && product.regular_price > product.price && (
                  <p className="text-sm text-muted-foreground line-through">
                    {formatCurrency(product.regular_price)}
                  </p>
                )}
              </div>
              <div className="text-sm">
                {product.stock_status === 'instock' ? (
                  <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                    In Stock
                  </Badge>
                ) : (
                  <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                    {product.stock_status === 'onbackorder' ? 'On Backorder' : 'Out of Stock'}
                  </Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// Helper function to get status badge color
function getStatusBadgeColor(status: ProductStatus) {
  switch (status) {
    case 'publish':
      return 'bg-green-500';
    case 'draft':
      return 'bg-gray-500';
    case 'pending':
      return 'bg-yellow-500';
    case 'private':
      return 'bg-blue-500';
    default:
      return 'bg-gray-500';
  }
}
