import { useState, useEffect, useRef } from "react";
import { Popover, PopoverContent, PopoverTrigger } from "./popover";
import { Button } from "./button";
import { Input } from "./input";
import { Label } from "./label";

interface ColorPickerProps {
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

export function ColorPicker({ value, onChange, className }: ColorPickerProps) {
  const [color, setColor] = useState(value || "#000000");
  const [open, setOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Update internal state when value prop changes
  useEffect(() => {
    setColor(value);
  }, [value]);

  // Handle color change
  const handleColorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newColor = e.target.value;
    setColor(newColor);
    onChange(newColor);
  };

  // Handle hex input change
  const handleHexChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let newColor = e.target.value;
    
    // Ensure it starts with #
    if (!newColor.startsWith("#")) {
      newColor = "#" + newColor;
    }
    
    // Only update if it's a valid hex color
    if (/^#([0-9A-F]{3}){1,2}$/i.test(newColor)) {
      setColor(newColor);
      onChange(newColor);
    } else {
      setColor(newColor);
    }
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={`h-8 w-8 rounded-md p-0 ${className}`}
          style={{ backgroundColor: color }}
          aria-label="Pick a color"
        />
      </PopoverTrigger>
      <PopoverContent className="w-64">
        <div className="space-y-2">
          <div className="flex justify-between">
            <Label htmlFor="color-picker">Color</Label>
            <div 
              className="h-4 w-8 rounded-sm" 
              style={{ backgroundColor: color }}
            />
          </div>
          <input
            ref={inputRef}
            type="color"
            id="color-picker"
            value={color}
            onChange={handleColorChange}
            className="h-8 w-full cursor-pointer appearance-none rounded-md border border-input bg-transparent p-0"
          />
          <div className="flex items-center gap-2">
            <Label htmlFor="hex-color">Hex</Label>
            <Input
              id="hex-color"
              value={color}
              onChange={handleHexChange}
              className="h-8 font-mono"
            />
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
