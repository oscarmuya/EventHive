"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload, X } from "lucide-react";

interface ImageUploadProps {
  label: string;
  id: string;
  required?: boolean;
  multiple?: boolean;
  value?: File | File[] | null;
  preview?: string | string[];
  onChange: (files: File | File[] | null) => void;
}

export function ImageUpload({
  label,
  id,
  required = false,
  multiple = false,
  value,
  preview,
  onChange,
}: ImageUploadProps) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    if (multiple) {
      onChange(Array.from(files));
    } else {
      onChange(files[0] || null);
    }
  };

  const handleRemove = (index?: number) => {
    if (multiple && Array.isArray(value) && typeof index === "number") {
      const newFiles = value.filter((_, i) => i !== index);
      onChange(newFiles.length > 0 ? newFiles : null);
    } else {
      onChange(null);
    }
  };

  const renderPreviews = () => {
    if (!preview) return null;

    if (multiple && Array.isArray(preview)) {
      return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          {preview.map((src, index) => (
            <div key={index} className="relative">
              <img
                src={src}
                alt={`Preview ${index + 1}`}
                className="w-full h-24 object-cover rounded-lg"
              />
              <Button
                type="button"
                variant="destructive"
                size="icon"
                className="absolute -top-2 -right-2 h-6 w-6"
                onClick={() => handleRemove(index)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      );
    }

    if (typeof preview === "string") {
      return (
        <div className="relative">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-48 object-cover rounded-lg"
          />
          <Button
            type="button"
            variant="destructive"
            size="icon"
            className="absolute top-2 right-2"
            onClick={() => handleRemove()}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="space-y-2">
      <Label>
        {label} {required && "*"}
      </Label>
      <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6">
        {preview ? (
          renderPreviews()
        ) : (
          <div className="text-center">
            <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
            <div className="mt-4">
              <Label htmlFor={id} className="cursor-pointer">
                <span className="mt-2 block text-sm font-medium text-muted-foreground">
                  Click to upload {multiple ? "images" : "image"}
                </span>
              </Label>
              <Input
                id={id}
                type="file"
                multiple={multiple}
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
                required={required}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
