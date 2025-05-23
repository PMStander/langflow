import { useState } from 'react';
import { crmApi } from '@/services/crm/crmApi';
import { useWorkspaceStore } from '@/stores/workspaceStore';
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
import { useToast } from '@/components/ui/use-toast';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircleIcon, CheckCircleIcon, ShoppingBagIcon, ShoppingCartIcon } from 'lucide-react';

interface EcommerceIntegrationProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

// Form schema for WooCommerce
const wooCommerceFormSchema = z.object({
  site_url: z.string().url('Please enter a valid URL'),
  consumer_key: z.string().min(1, 'Consumer key is required'),
  consumer_secret: z.string().min(1, 'Consumer secret is required'),
  limit: z.number().min(1).max(100).default(10),
});

// Form schema for Shopify
const shopifyFormSchema = z.object({
  shop_url: z.string().url('Please enter a valid URL'),
  access_token: z.string().min(1, 'Access token is required'),
  limit: z.number().min(1).max(100).default(10),
});

type WooCommerceFormValues = z.infer<typeof wooCommerceFormSchema>;
type ShopifyFormValues = z.infer<typeof shopifyFormSchema>;

export default function EcommerceIntegration({ isOpen, onClose, onSuccess }: EcommerceIntegrationProps) {
  const { toast } = useToast();
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);
  const [activeTab, setActiveTab] = useState<string>('woocommerce');
  const [isImporting, setIsImporting] = useState<boolean>(false);
  const [importResult, setImportResult] = useState<any>(null);
  
  // API hooks
  const [importWooCommerceProducts] = crmApi.useImportWooCommerceProductsMutation();
  const [importShopifyProducts] = crmApi.useImportShopifyProductsMutation();
  
  // WooCommerce form
  const wooCommerceForm = useForm<WooCommerceFormValues>({
    resolver: zodResolver(wooCommerceFormSchema),
    defaultValues: {
      site_url: '',
      consumer_key: '',
      consumer_secret: '',
      limit: 10,
    },
  });
  
  // Shopify form
  const shopifyForm = useForm<ShopifyFormValues>({
    resolver: zodResolver(shopifyFormSchema),
    defaultValues: {
      shop_url: '',
      access_token: '',
      limit: 10,
    },
  });
  
  // Handle WooCommerce import
  const handleWooCommerceImport = async (values: WooCommerceFormValues) => {
    if (!currentWorkspaceId) return;
    
    setIsImporting(true);
    setImportResult(null);
    
    try {
      const result = await importWooCommerceProducts({
        workspace_id: currentWorkspaceId,
        ...values,
      }).unwrap();
      
      setImportResult(result);
      
      if (result.success > 0) {
        toast({
          title: 'Import Successful',
          description: `Successfully imported ${result.success} products from WooCommerce with ${result.errors} errors.`,
        });
        onSuccess();
      } else {
        toast({
          title: 'Import Failed',
          description: `Failed to import products from WooCommerce. ${result.errors} errors occurred.`,
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error importing WooCommerce products:', error);
      toast({
        title: 'Import Failed',
        description: 'An error occurred while importing products from WooCommerce.',
        variant: 'destructive',
      });
    } finally {
      setIsImporting(false);
    }
  };
  
  // Handle Shopify import
  const handleShopifyImport = async (values: ShopifyFormValues) => {
    if (!currentWorkspaceId) return;
    
    setIsImporting(true);
    setImportResult(null);
    
    try {
      const result = await importShopifyProducts({
        workspace_id: currentWorkspaceId,
        ...values,
      }).unwrap();
      
      setImportResult(result);
      
      if (result.success > 0) {
        toast({
          title: 'Import Successful',
          description: `Successfully imported ${result.success} products from Shopify with ${result.errors} errors.`,
        });
        onSuccess();
      } else {
        toast({
          title: 'Import Failed',
          description: `Failed to import products from Shopify. ${result.errors} errors occurred.`,
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error importing Shopify products:', error);
      toast({
        title: 'Import Failed',
        description: 'An error occurred while importing products from Shopify.',
        variant: 'destructive',
      });
    } finally {
      setIsImporting(false);
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>E-commerce Integration</DialogTitle>
        </DialogHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-2 w-full">
            <TabsTrigger value="woocommerce">WooCommerce</TabsTrigger>
            <TabsTrigger value="shopify">Shopify</TabsTrigger>
          </TabsList>
          
          <TabsContent value="woocommerce" className="space-y-4 mt-4">
            <div className="flex items-center justify-center mb-4">
              <ShoppingCartIcon className="h-12 w-12 text-orange-500" />
            </div>
            
            <Form {...wooCommerceForm}>
              <form onSubmit={wooCommerceForm.handleSubmit(handleWooCommerceImport)} className="space-y-4">
                <FormField
                  control={wooCommerceForm.control}
                  name="site_url"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Site URL*</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="https://your-store.com" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={wooCommerceForm.control}
                  name="consumer_key"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Consumer Key*</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="ck_xxxxxxxxxxxxxxxxxxxx" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={wooCommerceForm.control}
                  name="consumer_secret"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Consumer Secret*</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="cs_xxxxxxxxxxxxxxxxxxxx" type="password" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={wooCommerceForm.control}
                  name="limit"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Product Limit</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type="number"
                          min={1}
                          max={100}
                          onChange={(e) => field.onChange(parseInt(e.target.value))}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <Button type="submit" className="w-full" disabled={isImporting}>
                  {isImporting ? 'Importing...' : 'Import Products'}
                </Button>
              </form>
            </Form>
          </TabsContent>
          
          <TabsContent value="shopify" className="space-y-4 mt-4">
            <div className="flex items-center justify-center mb-4">
              <ShoppingBagIcon className="h-12 w-12 text-green-500" />
            </div>
            
            <Form {...shopifyForm}>
              <form onSubmit={shopifyForm.handleSubmit(handleShopifyImport)} className="space-y-4">
                <FormField
                  control={shopifyForm.control}
                  name="shop_url"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Shop URL*</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="your-store.myshopify.com" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={shopifyForm.control}
                  name="access_token"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Access Token*</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="shpat_xxxxxxxxxxxxxxxxxxxx" type="password" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={shopifyForm.control}
                  name="limit"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Product Limit</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type="number"
                          min={1}
                          max={100}
                          onChange={(e) => field.onChange(parseInt(e.target.value))}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <Button type="submit" className="w-full" disabled={isImporting}>
                  {isImporting ? 'Importing...' : 'Import Products'}
                </Button>
              </form>
            </Form>
          </TabsContent>
        </Tabs>
        
        {importResult && (
          <Alert variant={importResult.success > 0 ? 'default' : 'destructive'} className="mt-4">
            <div className="flex items-start gap-2">
              {importResult.success > 0 ? (
                <CheckCircleIcon className="h-5 w-5 mt-0.5" />
              ) : (
                <AlertCircleIcon className="h-5 w-5 mt-0.5" />
              )}
              <AlertDescription>
                <p>
                  <strong>Import Results:</strong>
                </p>
                <ul className="list-disc list-inside mt-1">
                  <li>Successfully imported: {importResult.success}</li>
                  <li>Errors: {importResult.errors}</li>
                </ul>
                {importResult.errors > 0 && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-sm">View Error Details</summary>
                    <div className="mt-2 text-xs max-h-32 overflow-y-auto">
                      <pre className="whitespace-pre-wrap">
                        {JSON.stringify(importResult.error_details, null, 2)}
                      </pre>
                    </div>
                  </details>
                )}
              </AlertDescription>
            </div>
          </Alert>
        )}
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
