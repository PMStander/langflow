import { Button } from "@/components/ui/button";
import { useCustomNavigate } from "@/customization/hooks/use-custom-navigate";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import ShadTooltip from "@/components/common/shadTooltipComponent";
import { Users, Store } from "lucide-react";

/**
 * NavigationLinks Component
 * 
 * Renders navigation links in the app header
 */
export default function NavigationLinks(): JSX.Element {
  const navigate = useCustomNavigate();

  return (
    <div className="flex items-center gap-2">
      {/* CRM Link */}
      <ShadTooltip content="CRM Dashboard" side="bottom" styleClasses="z-10">
        <Button
          unstyled
          onClick={() => navigate("/crm/dashboard")}
          className="flex items-center gap-1 px-2 py-1 text-sm font-medium text-muted-foreground hover:text-primary"
          data-testid="crm-nav-link"
        >
          <Users className="h-4 w-4" />
          <span>CRM</span>
        </Button>
      </ShadTooltip>

      {/* Store Link */}
      <ShadTooltip content="Langflow Store" side="bottom" styleClasses="z-10">
        <Button
          unstyled
          onClick={() => navigate("/store")}
          className="flex items-center gap-1 px-2 py-1 text-sm font-medium text-muted-foreground hover:text-primary"
          data-testid="store-nav-link"
        >
          <Store className="h-4 w-4" />
          <span>Store</span>
        </Button>
      </ShadTooltip>
    </div>
  );
}
