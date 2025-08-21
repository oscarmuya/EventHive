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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { EventData } from "./types";
import { ImageUpload } from "./image-upload";

interface EventDetailsFormProps {
  event: EventData;
  onChange: (event: EventData) => void;
  coverImage: File | null;
  coverImagePreview: string;
  onCoverImageChange: (file: File | null) => void;
}

export function EventDetailsForm({
  event,
  onChange,
  coverImage,
  coverImagePreview,
  onCoverImageChange,
}: EventDetailsFormProps) {
  const updateField = (field: keyof EventData, value: string | number) => {
    onChange({ ...event, [field]: value });
  };

  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9 -]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .trim();
  };

  const handleTitleChange = (title: string) => {
    onChange({
      ...event,
      title,
      slug: generateSlug(title),
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Event Details</CardTitle>
        <CardDescription>Provide information about your event</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="event-title">Event Title *</Label>
            <Input
              id="event-title"
              value={event.title}
              onChange={(e) => handleTitleChange(e.target.value)}
              placeholder="Enter event title"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="event-slug">Event Slug *</Label>
            <Input
              id="event-slug"
              value={event.slug}
              onChange={(e) => updateField("slug", e.target.value)}
              placeholder="event-slug"
              required
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="event-description">Event Description *</Label>
          <Textarea
            id="event-description"
            value={event.description}
            onChange={(e) => updateField("description", e.target.value)}
            placeholder="Describe your event..."
            rows={4}
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="start-time">Start Date & Time *</Label>
            <Input
              id="start-time"
              type="datetime-local"
              value={event.start_time}
              onChange={(e) => updateField("start_time", e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="end-time">End Date & Time *</Label>
            <Input
              id="end-time"
              type="datetime-local"
              value={event.end_time}
              onChange={(e) => updateField("end_time", e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="event-capacity">Event Capacity *</Label>
            <Input
              id="event-capacity"
              type="number"
              value={event.capacity}
              onChange={(e) =>
                updateField("capacity", parseInt(e.target.value) || 0)
              }
              placeholder="Maximum attendees"
              required
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="event-status">Event Status</Label>
          <Select
            value={event.status}
            onValueChange={(value: "draft" | "published" | "cancelled") =>
              updateField("status", value)
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="published">Published</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <ImageUpload
          label="Event Cover Image"
          id="cover-image"
          required={true}
          value={coverImage}
          preview={coverImagePreview}
          //   @ts-ignore
          onChange={onCoverImageChange}
        />
      </CardContent>
    </Card>
  );
}
