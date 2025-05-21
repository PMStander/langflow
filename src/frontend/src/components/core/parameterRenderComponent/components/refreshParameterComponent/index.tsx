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
  const isButtonType = (type: any): boolean => {
    if (!type) return false;

    // Check if it's the Button component
    if (type === Button) return true;

    // Check displayName or name
    const displayName = type.displayName || type.name || '';
    if (displayName === 'Button') return true;

    // Check if name contains 'button' (case insensitive)
    if (displayName.toLowerCase().includes('button')) return true;

    // Check if it's an HTML button element
    if (type === 'button') return true;

    return false;
  };

  const checkIfContainsButton = (element: React.ReactNode): boolean => {
    if (!React.isValidElement(element)) return false;

    // Check if the element itself is a button
    if (isButtonType(element.type)) return true;

    // Check if it has a type="button" prop
    if (element.props?.type === 'button') return true;

    // Check if any of its children are buttons
    if (element.props?.children) {
      const children = React.Children.toArray(element.props.children);
      return children.some(child => checkIfContainsButton(child));
    }

    return false;
  };

  const childIsButton = React.Children.toArray(children).some(child =>
    checkIfContainsButton(child)
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
