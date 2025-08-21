"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
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
import { Plus, Trash2, Upload, X } from "lucide-react";

interface VenueData {
  name: string;
  description: string;
  address_1: string;
  address_2: string;
  city: string;
  region: string;
  country: string;
  postal_code: string;
  capacity: number;
}

interface EventData {
  title: string;
  slug: string;
  description: string;
  start_time: string;
  end_time: string;
  status: "draft" | "published" | "cancelled";
  capacity: number;
  cover_image_url: string;
}

interface TicketType {
  id: string;
  name: string;
  description: string;
  price: number;
  quantity_total: number;
  quantity_sold: number;
  sales_start: string;
  sales_end: string;
  per_person_limit: number;
  is_active: boolean;
}

interface CreateEventProps {
  onSubmit?: (data: {
    venue: VenueData;
    event: EventData;
    ticketTypes: TicketType[];
    images: { coverImage: File | null; venueImages: File[] };
  }) => void;
}

export default function CreateEvent({ onSubmit }: CreateEventProps) {
  const [venue, setVenue] = useState<VenueData>({
    name: "",
    description: "",
    address_1: "",
    address_2: "",
    city: "",
    region: "",
    country: "",
    postal_code: "",
    capacity: 0,
  });

  const [event, setEvent] = useState<EventData>({
    title: "",
    slug: "",
    description: "",
    start_time: "",
    end_time: "",
    status: "draft",
    capacity: 0,
    cover_image_url: "",
  });

  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([
    {
      id: "1",
      name: "",
      description: "",
      price: 0,
      quantity_total: 0,
      quantity_sold: 0,
      sales_start: "",
      sales_end: "",
      per_person_limit: 1,
      is_active: true,
    },
  ]);

  const [coverImage, setCoverImage] = useState<File | null>(null);
  const [venueImages, setVenueImages] = useState<File[]>([]);
  const [coverImagePreview, setCoverImagePreview] = useState<string>("");
  const [venueImagePreviews, setVenueImagePreviews] = useState<string[]>([]);

  // Generate slug from title
  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9 -]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .trim();
  };

  const handleEventTitleChange = (title: string) => {
    setEvent((prev) => ({
      ...prev,
      title,
      slug: generateSlug(title),
    }));
  };

  const handleCoverImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setCoverImage(file);
      const reader = new FileReader();
      reader.onload = () => setCoverImagePreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleVenueImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setVenueImages((prev) => [...prev, ...files]);

    files.forEach((file) => {
      const reader = new FileReader();
      reader.onload = () => {
        setVenueImagePreviews((prev) => [...prev, reader.result as string]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeVenueImage = (index: number) => {
    setVenueImages((prev) => prev.filter((_, i) => i !== index));
    setVenueImagePreviews((prev) => prev.filter((_, i) => i !== index));
  };

  const addTicketType = () => {
    const newTicket: TicketType = {
      id: Date.now().toString(),
      name: "",
      description: "",
      price: 0,
      quantity_total: 0,
      quantity_sold: 0,
      sales_start: "",
      sales_end: "",
      per_person_limit: 1,
      is_active: true,
    };
    setTicketTypes((prev) => [...prev, newTicket]);
  };

  const removeTicketType = (id: string) => {
    setTicketTypes((prev) => prev.filter((ticket) => ticket.id !== id));
  };

  const updateTicketType = (
    id: string,
    field: keyof TicketType,
    value: any
  ) => {
    setTicketTypes((prev) =>
      prev.map((ticket) =>
        ticket.id === id ? { ...ticket, [field]: value } : ticket
      )
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (onSubmit) {
      onSubmit({
        venue,
        event,
        ticketTypes,
        images: {
          coverImage,
          venueImages,
        },
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8 max-w-4xl mx-auto p-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold">Create New Event</h1>
        <p className="text-muted-foreground mt-2">
          Fill in the details below to create your event
        </p>
      </div>{" "}
      {/* Venue Details Section */}
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
                onChange={(e) =>
                  setVenue((prev) => ({ ...prev, name: e.target.value }))
                }
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
                  setVenue((prev) => ({
                    ...prev,
                    capacity: parseInt(e.target.value) || 0,
                  }))
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
              onChange={(e) =>
                setVenue((prev) => ({ ...prev, description: e.target.value }))
              }
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
                onChange={(e) =>
                  setVenue((prev) => ({ ...prev, address_1: e.target.value }))
                }
                placeholder="Street address"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="address-2">Address Line 2</Label>
              <Input
                id="address-2"
                value={venue.address_2}
                onChange={(e) =>
                  setVenue((prev) => ({ ...prev, address_2: e.target.value }))
                }
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
                onChange={(e) =>
                  setVenue((prev) => ({ ...prev, city: e.target.value }))
                }
                placeholder="City"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="region">State/Region *</Label>
              <Input
                id="region"
                value={venue.region}
                onChange={(e) =>
                  setVenue((prev) => ({ ...prev, region: e.target.value }))
                }
                placeholder="State or region"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="country">Country *</Label>
              <Input
                id="country"
                value={venue.country}
                onChange={(e) =>
                  setVenue((prev) => ({ ...prev, country: e.target.value }))
                }
                placeholder="Country"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="postal-code">Postal Code *</Label>
              <Input
                id="postal-code"
                value={venue.postal_code}
                onChange={(e) =>
                  setVenue((prev) => ({ ...prev, postal_code: e.target.value }))
                }
                placeholder="ZIP/Postal code"
                required
              />
            </div>
          </div>

          {/* Venue Images */}
          <div className="space-y-2">
            <Label>Venue Images</Label>
            <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6">
              <div className="text-center">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
                <div className="mt-4">
                  <Label htmlFor="venue-images" className="cursor-pointer">
                    <span className="mt-2 block text-sm font-medium text-muted-foreground">
                      Click to upload venue images
                    </span>
                  </Label>
                  <Input
                    id="venue-images"
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleVenueImagesChange}
                    className="hidden"
                  />
                </div>
              </div>
            </div>
            {venueImagePreviews.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                {venueImagePreviews.map((preview, index) => (
                  <div key={index} className="relative">
                    <img
                      src={preview}
                      alt={`Venue ${index + 1}`}
                      className="w-full h-24 object-cover rounded-lg"
                    />
                    <Button
                      type="button"
                      variant="destructive"
                      size="icon"
                      className="absolute -top-2 -right-2 h-6 w-6"
                      onClick={() => removeVenueImage(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      {/* Event Details Section */}
      <Card>
        <CardHeader>
          <CardTitle>Event Details</CardTitle>
          <CardDescription>
            Provide information about your event
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="event-title">Event Title *</Label>
              <Input
                id="event-title"
                value={event.title}
                onChange={(e) => handleEventTitleChange(e.target.value)}
                placeholder="Enter event title"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="event-slug">Event Slug *</Label>
              <Input
                id="event-slug"
                value={event.slug}
                onChange={(e) =>
                  setEvent((prev) => ({ ...prev, slug: e.target.value }))
                }
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
              onChange={(e) =>
                setEvent((prev) => ({ ...prev, description: e.target.value }))
              }
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
                onChange={(e) =>
                  setEvent((prev) => ({ ...prev, start_time: e.target.value }))
                }
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="end-time">End Date & Time *</Label>
              <Input
                id="end-time"
                type="datetime-local"
                value={event.end_time}
                onChange={(e) =>
                  setEvent((prev) => ({ ...prev, end_time: e.target.value }))
                }
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
                  setEvent((prev) => ({
                    ...prev,
                    capacity: parseInt(e.target.value) || 0,
                  }))
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
                setEvent((prev) => ({ ...prev, status: value }))
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

          {/* Cover Image */}
          <div className="space-y-2">
            <Label>Event Cover Image *</Label>
            <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6">
              {coverImagePreview ? (
                <div className="relative">
                  <img
                    src={coverImagePreview}
                    alt="Cover preview"
                    className="w-full h-48 object-cover rounded-lg"
                  />
                  <Button
                    type="button"
                    variant="destructive"
                    size="icon"
                    className="absolute top-2 right-2"
                    onClick={() => {
                      setCoverImage(null);
                      setCoverImagePreview("");
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div className="text-center">
                  <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
                  <div className="mt-4">
                    <Label htmlFor="cover-image" className="cursor-pointer">
                      <span className="mt-2 block text-sm font-medium text-muted-foreground">
                        Click to upload cover image
                      </span>
                    </Label>
                    <Input
                      id="cover-image"
                      type="file"
                      accept="image/*"
                      onChange={handleCoverImageChange}
                      className="hidden"
                      required
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
      {/* Ticket Types Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Ticket Types
            <Button type="button" onClick={addTicketType} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Add Ticket Type
            </Button>
          </CardTitle>
          <CardDescription>
            Configure different ticket types for your event
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {ticketTypes.map((ticket, index) => (
            <div key={ticket.id} className="border rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Ticket Type {index + 1}</h4>
                {ticketTypes.length > 1 && (
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    onClick={() => removeTicketType(ticket.id)}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Remove
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Ticket Name *</Label>
                  <Input
                    value={ticket.name}
                    onChange={(e) =>
                      updateTicketType(ticket.id, "name", e.target.value)
                    }
                    placeholder="e.g., General Admission"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Price *</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={ticket.price}
                    onChange={(e) =>
                      updateTicketType(
                        ticket.id,
                        "price",
                        parseFloat(e.target.value) || 0
                      )
                    }
                    placeholder="0.00"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Description</Label>
                <Textarea
                  value={ticket.description}
                  onChange={(e) =>
                    updateTicketType(ticket.id, "description", e.target.value)
                  }
                  placeholder="Describe this ticket type..."
                  rows={2}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Total Quantity *</Label>
                  <Input
                    type="number"
                    value={ticket.quantity_total}
                    onChange={(e) =>
                      updateTicketType(
                        ticket.id,
                        "quantity_total",
                        parseInt(e.target.value) || 0
                      )
                    }
                    placeholder="Available tickets"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Sold Quantity</Label>
                  <Input
                    type="number"
                    value={ticket.quantity_sold}
                    onChange={(e) =>
                      updateTicketType(
                        ticket.id,
                        "quantity_sold",
                        parseInt(e.target.value) || 0
                      )
                    }
                    placeholder="Tickets sold"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Per Person Limit</Label>
                  <Input
                    type="number"
                    value={ticket.per_person_limit}
                    onChange={(e) =>
                      updateTicketType(
                        ticket.id,
                        "per_person_limit",
                        parseInt(e.target.value) || 1
                      )
                    }
                    placeholder="Max per person"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Sales Start Date & Time *</Label>
                  <Input
                    type="datetime-local"
                    value={ticket.sales_start}
                    onChange={(e) =>
                      updateTicketType(ticket.id, "sales_start", e.target.value)
                    }
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Sales End Date & Time *</Label>
                  <Input
                    type="datetime-local"
                    value={ticket.sales_end}
                    onChange={(e) =>
                      updateTicketType(ticket.id, "sales_end", e.target.value)
                    }
                    required
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id={`active-${ticket.id}`}
                  checked={ticket.is_active}
                  onChange={(e) =>
                    updateTicketType(ticket.id, "is_active", e.target.checked)
                  }
                  className="rounded border-gray-300"
                />
                <Label htmlFor={`active-${ticket.id}`}>
                  Active (available for sale)
                </Label>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
      {/* Submit Button */}
      <div className="flex justify-end space-x-4">
        <Button type="button" variant="outline">
          Save as Draft
        </Button>
        <Button type="submit">Create Event</Button>
      </div>
    </form>
  );
}
