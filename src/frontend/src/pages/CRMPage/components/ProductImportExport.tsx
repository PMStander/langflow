import { useState, useRef } from 'react';
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
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/components/ui/use-toast';
import { UploadIcon, DownloadIcon, FileIcon, AlertCircleIcon, CheckCircleIcon } from 'lucide-react';

interface ProductImportExportProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ProductImportExport({ isOpen, onClose }: ProductImportExportProps) {
  const { toast } = useToast();
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);
  const [activeTab, setActiveTab] = useState<string>('import');
  const [importFormat, setImportFormat] = useState<'csv' | 'json'>('csv');
  const [exportFormat, setExportFormat] = useState<'csv' | 'json'>('csv');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [importResult, setImportResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // API hooks
  const [importProducts] = crmApi.useImportProductsMutation();
  const exportProductsQuery = crmApi.useExportProductsQuery(
    { workspace_id: currentWorkspaceId || '', format: exportFormat },
    { skip: true }
  );

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setImportResult(null);
    }
  };

  // Handle file upload button click
  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Handle import
  const handleImport = async () => {
    if (!selectedFile || !currentWorkspaceId) return;

    setIsUploading(true);
    setImportResult(null);

    try {
      const result = await importProducts({
        workspace_id: currentWorkspaceId,
        file: selectedFile,
        format: importFormat,
      }).unwrap();

      setImportResult(result);

      if (result.success > 0) {
        toast({
          title: 'Import Successful',
          description: `Successfully imported ${result.success} products with ${result.errors} errors.`,
        });
      } else {
        toast({
          title: 'Import Failed',
          description: `Failed to import products. ${result.errors} errors occurred.`,
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error importing products:', error);
      toast({
        title: 'Import Failed',
        description: 'An error occurred while importing products.',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  // Handle export
  const handleExport = async () => {
    if (!currentWorkspaceId) return;

    try {
      const blob = await exportProductsQuery.refetch().unwrap();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `products.${exportFormat}`;
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast({
        title: 'Export Successful',
        description: `Products exported successfully as ${exportFormat.toUpperCase()}.`,
      });
    } catch (error) {
      console.error('Error exporting products:', error);
      toast({
        title: 'Export Failed',
        description: 'An error occurred while exporting products.',
        variant: 'destructive',
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Import/Export Products</DialogTitle>
        </DialogHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-2 w-full">
            <TabsTrigger value="import">Import</TabsTrigger>
            <TabsTrigger value="export">Export</TabsTrigger>
          </TabsList>
          
          <TabsContent value="import" className="space-y-4 mt-4">
            <div className="space-y-2">
              <Label>File Format</Label>
              <Select
                value={importFormat}
                onValueChange={(value) => setImportFormat(value as 'csv' | 'json')}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select format" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">CSV</SelectItem>
                  <SelectItem value="json">JSON</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Select File</Label>
              <Input
                ref={fileInputRef}
                type="file"
                accept={importFormat === 'csv' ? '.csv' : '.json'}
                onChange={handleFileChange}
                className="hidden"
              />
              <div 
                className="border-2 border-dashed rounded-md p-6 text-center cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={handleUploadClick}
              >
                {selectedFile ? (
                  <div className="flex items-center justify-center gap-2">
                    <FileIcon className="h-5 w-5" />
                    <span>{selectedFile.name}</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center gap-2">
                    <UploadIcon className="h-8 w-8 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                      Click to select a {importFormat.toUpperCase()} file
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            {importResult && (
              <Alert variant={importResult.success > 0 ? 'default' : 'destructive'}>
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
          </TabsContent>
          
          <TabsContent value="export" className="space-y-4 mt-4">
            <div className="space-y-2">
              <Label>File Format</Label>
              <Select
                value={exportFormat}
                onValueChange={(value) => setExportFormat(value as 'csv' | 'json')}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select format" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">CSV</SelectItem>
                  <SelectItem value="json">JSON</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="text-center py-4">
              <p className="text-sm text-muted-foreground mb-4">
                Export all products from the current workspace as a {exportFormat.toUpperCase()} file.
              </p>
              <Button
                onClick={handleExport}
                className="w-full"
                disabled={exportProductsQuery.isFetching}
              >
                <DownloadIcon className="h-4 w-4 mr-2" />
                {exportProductsQuery.isFetching ? 'Exporting...' : 'Export Products'}
              </Button>
            </div>
          </TabsContent>
        </Tabs>
        
        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          {activeTab === 'import' && (
            <Button
              onClick={handleImport}
              disabled={!selectedFile || isUploading}
            >
              {isUploading ? 'Importing...' : 'Import Products'}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
