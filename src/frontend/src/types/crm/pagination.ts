/**
 * Types for paginated responses in the CRM module.
 */

import { Client, Invoice, Opportunity, Task } from ".";

/**
 * Pagination metadata for paginated responses.
 */
export interface PaginationMetadata {
  /** Total number of items */
  total: number;
  /** Current page number (1-based) */
  page: number;
  /** Number of items per page */
  size: number;
  /** Total number of pages */
  pages: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_prev: boolean;
  /** Next page number */
  next_page: number | null;
  /** Previous page number */
  prev_page: number | null;
}

/**
 * Generic paginated response interface.
 */
export interface PaginatedResponse<T> {
  /** List of items */
  items: T[];
  /** Pagination metadata */
  metadata: PaginationMetadata;
}

/**
 * Type aliases for specific paginated responses.
 */
export type PaginatedClients = PaginatedResponse<Client>;
export type PaginatedInvoices = PaginatedResponse<Invoice>;
export type PaginatedOpportunities = PaginatedResponse<Opportunity>;
export type PaginatedTasks = PaginatedResponse<Task>;

/**
 * Pagination parameters for API requests.
 */
export interface PaginationParams {
  /** Number of records to skip (offset) */
  skip?: number;
  /** Maximum number of records to return */
  limit?: number;
  /** Page number (1-based, alternative to skip) */
  page?: number;
}

/**
 * Utility function to extract items from a paginated response.
 * This helps maintain backward compatibility with code that expects an array of items.
 * 
 * @param response The paginated response
 * @returns The items from the paginated response
 */
export function extractItems<T>(response: PaginatedResponse<T> | T[]): T[] {
  if (Array.isArray(response)) {
    return response;
  }
  return response.items;
}

/**
 * Utility function to extract pagination metadata from a paginated response.
 * 
 * @param response The paginated response
 * @returns The pagination metadata or null if the response is not paginated
 */
export function extractMetadata<T>(response: PaginatedResponse<T> | T[]): PaginationMetadata | null {
  if (Array.isArray(response)) {
    return null;
  }
  return response.metadata;
}

/**
 * Utility function to check if a response is paginated.
 * 
 * @param response The response to check
 * @returns True if the response is paginated, false otherwise
 */
export function isPaginated<T>(response: PaginatedResponse<T> | T[]): response is PaginatedResponse<T> {
  return !Array.isArray(response) && 'items' in response && 'metadata' in response;
}
