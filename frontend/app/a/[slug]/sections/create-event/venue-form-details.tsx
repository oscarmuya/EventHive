"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { VenueData } from "./types";
import { ImageUpload } from "./image-upload";

interface VenueDetailsFormProps {
  venue: VenueData;
  onChange: (venue: VenueData) => void;
  venueImages: File[];
  venueImagePreviews: string[];
  onVenueImagesChange: (files: File[]) => void;
}

export function VenueDetailsForm({
  venue,
  onChange,
  venueImages,
  venueImagePreviews,
  onVenueImagesChange,
}: VenueDetailsFormProps) {
  const updateField = (field: keyof VenueData, value: string | number) => {
    onChange({ ...venue, [field]: value });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Venue Details</CardTitle>
        <CardDescription>
          Provide information about the venue where your event will take place
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="venue-name">Venue Name *</Label>
            <Input
              id="venue-name"
              value={venue.name}
              onChange={(e) => updateField("name", e.target.value)}
              placeholder="Enter venue name"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="venue-capacity">Venue Capacity *</Label>
            <Input
              id="venue-capacity"
              type="number"
              value={venue.capacity}
              onChange={(e) =>
                updateField("capacity", parseInt(e.target.value) || 0)
              }
              placeholder="Maximum capacity"
              required
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="venue-description">Venue Description</Label>
          <Textarea
            id="venue-description"
            value={venue.description}
            onChange={(e) => updateField("description", e.target.value)}
            placeholder="Describe the venue..."
            rows={3}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="address-1">Address Line 1 *</Label>
            <Input
              id="address-1"
              value={venue.address_1}
              onChange={(e) => updateField("address_1", e.target.value)}
              placeholder="Street address"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="address-2">Address Line 2</Label>
            <Input
              id="address-2"
              value={venue.address_2}
              onChange={(e) => updateField("address_2", e.target.value)}
              placeholder="Apartment, suite, etc."
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <Label htmlFor="city">City *</Label>
            <Input
              id="city"
              value={venue.city}
              onChange={(e) => updateField("city", e.target.value)}
              placeholder="City"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="region">State/Region *</Label>
            <Input
              id="region"
              value={venue.region}
              onChange={(e) => updateField("region", e.target.value)}
              placeholder="State or region"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="country">Country *</Label>
            <Input
              id="country"
              value={venue.country}
              onChange={(e) => updateField("country", e.target.value)}
              placeholder="Country"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="postal-code">Postal Code *</Label>
            <Input
              id="postal-code"
              value={venue.postal_code}
              onChange={(e) => updateField("postal_code", e.target.value)}
              placeholder="ZIP/Postal code"
              required
            />
          </div>
        </div>

        <ImageUpload
          label="Venue Images"
          id="venue-images"
          multiple={true}
          value={venueImages}
          preview={venueImagePreviews}
          onChange={(files) => onVenueImagesChange(files as File[])}
        />
      </CardContent>
    </Card>
  );
}
