import * as DialogPrimitive from "@radix-ui/react-dialog";
import { DialogContent } from "@radix-ui/react-dialog";
import React from "react";
import { cn } from "../../utils/utils";
import { Cross2Icon } from "@radix-ui/react-icons";
import ShadTooltip from "../../components/common/shadTooltipComponent";

// Create a VisuallyHidden component for accessibility
const VisuallyHidden = React.forwardRef<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement>
>(({ children, ...props }, ref) => (
  <span
    ref={ref}
    className="absolute h-px w-px overflow-hidden whitespace-nowrap border-0 p-0"
    style={{ clip: "rect(0 0 0 0)", clipPath: "inset(50%)" }}
    {...props}
  >
    {children}
  </span>
));
VisuallyHidden.displayName = "VisuallyHidden";

// Create a DialogTitle component
const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className,
    )}
    {...props}
  />
));
DialogTitle.displayName = DialogPrimitive.Title.displayName;

export const DialogContentWithouFixed = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content> & {
    hideTitle?: boolean;
    closeButtonClassName?: string;
  }
>(
  (
    { className, children, hideTitle = false, closeButtonClassName, ...props },
    ref,
  ) => {
    // Check if DialogTitle is included in children
    const hasDialogTitle = React.Children.toArray(children).some(
      (child) => React.isValidElement(child) && child.type === DialogTitle
    );

    return (
      <DialogPrimitive.Content
        ref={ref}
        className={cn(
          "z-50 flex w-full max-w-lg flex-col gap-4 rounded-xl border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%]",
          className,
        )}
        aria-describedby="dialog-description"
        {...props}
      >
        {!hasDialogTitle && (
          <VisuallyHidden>
            <DialogTitle>Dialog</DialogTitle>
          </VisuallyHidden>
        )}
        {children}
        <VisuallyHidden id="dialog-description">
          Dialog content for accessibility
        </VisuallyHidden>
        <ShadTooltip
          styleClasses="z-50"
          content="Close"
          side="bottom"
          avoidCollisions
        >
          <DialogPrimitive.Close
            className={cn(
              "absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-sm ring-offset-background transition-opacity hover:bg-secondary-hover hover:text-accent-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground",
              closeButtonClassName,
            )}
          >
            <Cross2Icon className="h-[18px] w-[18px]" />
            <span className="sr-only">Close</span>
          </DialogPrimitive.Close>
        </ShadTooltip>
      </DialogPrimitive.Content>
    );
  },
);
DialogContentWithouFixed.displayName = DialogPrimitive.Content.displayName;

export default DialogContentWithouFixed;
