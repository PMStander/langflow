/**
 * Utility functions for exporting data to various formats
 */

/**
 * Export data to CSV format
 * @param data Array of objects to export
 * @param filename Filename for the exported file
 */
export const exportToCSV = (data: any[], filename: string) => {
  if (!data || !data.length) {
    console.error('No data to export');
    return;
  }

  // Get headers from the first object
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    // Headers row
    headers.join(','),
    // Data rows
    ...data.map(row => 
      headers.map(header => {
        const value = row[header];
        // Handle different data types
        if (value === null || value === undefined) {
          return '';
        } else if (typeof value === 'object') {
          // For dates or complex objects
          if (value instanceof Date) {
            return `"${value.toISOString()}"`;
          } else {
            return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
          }
        } else if (typeof value === 'string') {
          // Escape quotes in strings
          return `"${value.replace(/"/g, '""')}"`;
        } else {
          return value;
        }
      }).join(',')
    )
  ].join('\n');
  
  // Create a blob and download link
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Export data to JSON format
 * @param data Data to export
 * @param filename Filename for the exported file
 */
export const exportToJSON = (data: any, filename: string) => {
  if (!data) {
    console.error('No data to export');
    return;
  }
  
  // Create a blob and download link
  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}.json`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Format data for export by cleaning up complex objects and formatting dates
 * @param data Raw data to format
 * @returns Formatted data ready for export
 */
export const formatDataForExport = (data: any[], entityType: string) => {
  if (!data || !data.length) return [];
  
  return data.map(item => {
    const formattedItem: Record<string, any> = {};
    
    // Process each field based on entity type
    Object.entries(item).forEach(([key, value]) => {
      // Skip internal fields
      if (key.startsWith('_')) return;
      
      // Format dates
      if (value instanceof Date || (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(value))) {
        formattedItem[key] = value instanceof Date 
          ? value.toISOString().split('T')[0] 
          : new Date(value).toISOString().split('T')[0];
        return;
      }
      
      // Format based on entity type and field
      if (entityType === 'client') {
        if (key === 'status') {
          formattedItem[key] = value ? String(value).charAt(0).toUpperCase() + String(value).slice(1) : '';
        } else {
          formattedItem[key] = value;
        }
      } else if (entityType === 'invoice') {
        if (key === 'status') {
          formattedItem[key] = value ? String(value).charAt(0).toUpperCase() + String(value).slice(1) : '';
        } else if (key === 'amount') {
          formattedItem[key] = typeof value === 'number' ? value.toFixed(2) : value;
        } else {
          formattedItem[key] = value;
        }
      } else if (entityType === 'opportunity') {
        if (key === 'status') {
          formattedItem[key] = value ? String(value).charAt(0).toUpperCase() + String(value).slice(1) : '';
        } else if (key === 'value') {
          formattedItem[key] = typeof value === 'number' ? value.toFixed(2) : value;
        } else {
          formattedItem[key] = value;
        }
      } else if (entityType === 'task') {
        if (key === 'status' || key === 'priority') {
          formattedItem[key] = value ? String(value).charAt(0).toUpperCase() + String(value).slice(1) : '';
        } else {
          formattedItem[key] = value;
        }
      } else {
        // Default handling
        formattedItem[key] = value;
      }
    });
    
    return formattedItem;
  });
};

/**
 * Export entity data to the specified format
 * @param data Data to export
 * @param entityType Type of entity (client, invoice, etc.)
 * @param format Export format (csv, json)
 */
export const exportEntityData = (data: any[], entityType: string, format: 'csv' | 'json' = 'csv') => {
  if (!data || !data.length) {
    console.error('No data to export');
    return;
  }
  
  // Format data for export
  const formattedData = formatDataForExport(data, entityType);
  
  // Generate filename
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
  const filename = `${entityType}_export_${timestamp}`;
  
  // Export based on format
  if (format === 'csv') {
    exportToCSV(formattedData, filename);
  } else if (format === 'json') {
    exportToJSON(formattedData, filename);
  }
};
