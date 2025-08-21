import { useState } from "react";

export function useImageUpload() {
  const [coverImage, setCoverImage] = useState<File | null>(null);
  const [coverImagePreview, setCoverImagePreview] = useState<string>("");
  const [venueImages, setVenueImages] = useState<File[]>([]);
  const [venueImagePreviews, setVenueImagePreviews] = useState<string[]>([]);

  const handleCoverImageChange = (file: File | null) => {
    if (file) {
      setCoverImage(file);
      const reader = new FileReader();
      reader.onload = () => setCoverImagePreview(reader.result as string);
      reader.readAsDataURL(file);
    } else {
      setCoverImage(null);
      setCoverImagePreview("");
    }
  };

  const handleVenueImagesChange = (files: File[]) => {
    setVenueImages(files);

    // Clear existing previews and create new ones
    setVenueImagePreviews([]);

    files.forEach((file) => {
      const reader = new FileReader();
      reader.onload = () => {
        setVenueImagePreviews((prev) => [...prev, reader.result as string]);
      };
      reader.readAsDataURL(file);
    });
  };

  return {
    coverImage,
    coverImagePreview,
    venueImages,
    venueImagePreviews,
    handleCoverImageChange,
    handleVenueImagesChange,
  };
}
