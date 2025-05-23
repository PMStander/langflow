# CRM Frontend Pagination Implementation Guide

## Overview

This document provides guidance on implementing the enhanced pagination features in the frontend components of the CRM module. The backend API has been updated to return paginated responses with metadata, and the frontend needs to be updated to handle these new response formats while maintaining backward compatibility.

## New Pagination Response Format

The backend API now returns paginated responses in the following format:

```typescript
interface PaginationMetadata {
  total: number;       // Total number of items
  page: number;        // Current page number (1-based)
  size: number;        // Number of items per page
  pages: number;       // Total number of pages
  has_next: boolean;   // Whether there is a next page
  has_prev: boolean;   // Whether there is a previous page
  next_page: number | null;  // Next page number
  prev_page: number | null;  // Previous page number
}

interface PaginatedResponse<T> {
  items: T[];          // List of items
  metadata: PaginationMetadata;  // Pagination metadata
}
```

## Implementation Steps

### 1. Update API Query Hooks

The API query hooks have been updated to handle both the new paginated response format and the old array format for backward compatibility. The hooks now use the `extractItems` and `extractMetadata` utility functions to handle both formats.

```typescript
// Example of updated API query hook
export const useGetClients = (params?: { workspace_id?: string; status?: string } & PaginationParams) => {
  return useQuery<PaginatedClients | Client[]>({
    queryKey: ['clients', params],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/clients', { params });
      return response.data;
    },
    select: (data) => {
      // Handle both paginated and non-paginated responses for backward compatibility
      if (isPaginated(data)) {
        return data;
      }
      // If it's an array, it's the old format
      return {
        items: data,
        metadata: {
          total: data.length,
          page: 1,
          size: data.length,
          pages: 1,
          has_next: false,
          has_prev: false,
          next_page: null,
          prev_page: null
        }
      };
    }
  });
};
```

### 2. Update Component State

Components that use the API query hooks need to be updated to handle the new response format. This includes:

- Updating state variables to store pagination metadata
- Adding pagination controls to the UI
- Handling pagination events

```typescript
// Example of updated component state
const [pageIndex, setPageIndex] = useState(1);
const [pageSize, setPageSize] = useState(10);

// Fetch clients with pagination
const { data: clientsResponse, isLoading } = useGetClientsQuery(
  currentWorkspaceId
    ? {
        workspace_id: currentWorkspaceId,
        status: clientFilters.status,
        page: pageIndex,
        limit: pageSize
      }
    : undefined,
  {
    enabled: !!currentWorkspaceId,
  }
);

// Extract clients and pagination metadata
const clients = clientsResponse ? extractItems(clientsResponse) : [];
const paginationMetadata = clientsResponse ? extractMetadata(clientsResponse) : null;
```

### 3. Add Pagination Controls

Add the `PaginatorComponent` to the UI to allow users to navigate between pages:

```tsx
{/* Pagination */}
{!isLoading && paginationMetadata && (
  <div className="mt-4">
    <PaginatorComponent
      pageIndex={paginationMetadata.page}
      pageSize={paginationMetadata.size}
      totalRowsCount={paginationMetadata.total}
      paginate={handlePageChange}
      pages={paginationMetadata.pages}
    />
  </div>
)}
```

### 4. Handle Pagination Events

Add a handler function to handle pagination events:

```typescript
// Handle pagination change
const handlePageChange = (newPageIndex: number, newPageSize: number) => {
  setPageIndex(newPageIndex);
  setPageSize(newPageSize);
};
```

### 5. Reset Pagination on Filter Changes

When filters change, reset the pagination to the first page:

```typescript
// Handle status filter
const handleStatusFilter = (status?: string) => {
  setClientFilters({ status: status as ClientStatus | undefined });
  // Reset pagination when filter changes
  setPageIndex(1);
};
```

## Backward Compatibility

The implementation maintains backward compatibility with existing code by:

1. Handling both the new paginated response format and the old array format
2. Providing utility functions to extract items and metadata from responses
3. Defaulting to reasonable values when metadata is not available

## Performance Considerations

1. **Caching**: The backend API now caches frequently accessed dashboard statistics. The frontend should take advantage of this by:
   - Setting appropriate cache times in the API query hooks
   - Implementing client-side caching for dashboard components
   - Using stale-while-revalidate patterns for dashboard data

2. **Optimistic Updates**: Implement optimistic updates for create, update, and delete operations to improve perceived performance:
   - Update the local cache immediately when a mutation is triggered
   - Revert the change if the mutation fails
   - Refetch the data after the mutation succeeds

3. **Lazy Loading**: Implement lazy loading for components that are not immediately visible:
   - Load dashboard components only when they are visible
   - Defer loading of detailed information until needed
   - Use skeleton loaders to improve perceived performance

## Testing

1. Test the pagination controls with different page sizes and page counts
2. Test navigation between pages (first, next, previous, last)
3. Test that filters work correctly with pagination
4. Test that the UI correctly displays the total count and current page
5. Test that the UI handles empty result sets correctly

## Example Implementation

See the updated `ClientsPage.tsx` component for a complete example of how to implement pagination in a CRM component.
