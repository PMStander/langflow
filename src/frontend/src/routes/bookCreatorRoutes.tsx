import { Route } from "react-router-dom";
import BookCreatorPage from "../pages/BookCreatorPage";
import BookEditorPage from "../pages/BookEditorPage";

/**
 * Book Creator Routes definition
 *
 * This function returns the route definitions for the Book Creator module
 * including the main Book Creator page and the Book Editor page
 */
export const BookCreatorRoutes = () => {
  return (
    <>
      <Route path="book-creator" element={<BookCreatorPage />} />
      <Route path="book-editor/:bookId" element={<BookEditorPage />} />
    </>
  );
};

export default BookCreatorRoutes;
