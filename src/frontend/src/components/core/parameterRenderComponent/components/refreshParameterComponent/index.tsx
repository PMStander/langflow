import { RefreshButton } from "@/components/ui/refreshButton";
import { Button } from "@/components/ui/button";
import { FLEX_VIEW_TYPES } from "@/constants/constants";
import { usePostTemplateValue } from "@/controllers/API/queries/nodes/use-post-template-value";
import { mutateTemplate } from "@/CustomNodes/helpers/mutate-template";
import useAlertStore from "@/stores/alertStore";
import { APIClassType, InputFieldType } from "@/types/api";
import { cn } from "@/utils/utils";
import * as React from "react";
import { InputProps } from "../../types";

export function RefreshParameterComponent({
  children,
  templateData,
  disabled,
  nodeClass,
  editNode,
  handleNodeClass,
  nodeId,
  name,
}: {
  children: React.ReactElement<InputProps>;
  templateData: Partial<InputFieldType>;
  disabled: boolean;
  nodeClass: APIClassType;
  editNode: boolean;
  handleNodeClass: (value: any, code?: string, type?: string) => void;
  nodeId: string;
  name: string;
}) {
  const postTemplateValue = usePostTemplateValue({
    parameterId: name,
    nodeId: nodeId,
    node: nodeClass,
  });

  const setErrorData = useAlertStore((state) => state.setErrorData);
  const handleRefreshButtonPress = () =>
    mutateTemplate(
      templateData.value,
      nodeId,
      nodeClass,
      handleNodeClass,
      postTemplateValue,
      setErrorData,
    );

  const isFlexView = FLEX_VIEW_TYPES.includes(templateData.type ?? "");

  // If this is a button type component or if the component renders a button, we should avoid adding another button
  const hasButtonType = templateData.type === "button" || templateData.type === "custom_button";

  // Create a wrapper div to avoid nesting buttons when the child is itself a button
  // Enhanced detection to check all possible button-like components
  const childIsButton = React.Children.toArray(children).some(
    (child) => {
      if (!React.isValidElement(child)) return false;
      
      // Check for Button component by displayName or name
      if ((child.type as any)?.displayName === 'Button' || 
          (child.type as any)?.name === 'Button' ||
          (child.type as any) === Button) return true;
      
      // Check for button HTML type
      if (child.props?.type === 'button') return true;
      
      // Check for button element
      if ((child.type as any) === 'button') return true;
      
      // Check component name contains "button" (case insensitive)
      const componentName = ((child.type as any)?.displayName || (child.type as any)?.name || '').toLowerCase();
      if (componentName.includes('button')) return true;
      
      // Check if any children are buttons (checking one level deep)
      if (child.props?.children) {
        const childChildren = React.Children.toArray(child.props.children);
        return childChildren.some(
          (grandChild) => 
            React.isValidElement(grandChild) && 
            ((grandChild.type as any)?.displayName === 'Button' || 
             (grandChild.type as any)?.name === 'Button' ||
             (grandChild.type as any) === Button ||
             (grandChild.props?.type === 'button') ||
             (grandChild.type as any) === 'button' ||
             ((grandChild.type as any)?.displayName || (grandChild.type as any)?.name || '').toLowerCase().includes('button'))
        );
      }
      
      return false;
    }
  );

  return (
    (children ||
      (templateData.refresh_button && !templateData.dialog_inputs)) && (
      <div
        className={cn(
          "flex w-full items-center justify-center gap-3",
          isFlexView ? "justify-end" : "justify-center",
        )}
      >
        {children}
        {templateData.refresh_button &&
          !templateData.dialog_inputs?.fields?.data?.node?.template &&
          !hasButtonType &&
          !childIsButton && (
            <div className="shrink-0 flex-col">
              <RefreshButton
                isLoading={postTemplateValue.isPending}
                disabled={disabled}
                editNode={editNode}
                button_text={templateData.refresh_button_text}
                handleUpdateValues={handleRefreshButtonPress}
                id={"refresh-button-" + name}
              />
            </div>
          )}
      </div>
    )
  );
}
