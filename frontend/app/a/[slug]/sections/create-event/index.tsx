"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { VenueData, EventData, TicketType } from "./types";
import { VenueDetailsForm } from "./venue-form-details";
import { EventDetailsForm } from "./event-details-form";
import { TicketTypesForm } from "./tickets-types-form";
import { useImageUpload } from "./use-image-upload";

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

  const {
    coverImage,
    coverImagePreview,
    venueImages,
    venueImagePreviews,
    handleCoverImageChange,
    handleVenueImagesChange,
  } = useImageUpload();

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
    <form onSubmit={handleSubmit} className="space-y-8 p-6 px-10">
      <div className="text-start">
        <h1 className="text-3xl font-bold">Create New Event</h1>
        <p className="text-muted-foreground mt-2">
          Fill in the details below to create your event
        </p>
      </div>

      <VenueDetailsForm
        venue={venue}
        onChange={setVenue}
        venueImages={venueImages}
        venueImagePreviews={venueImagePreviews}
        onVenueImagesChange={handleVenueImagesChange}
      />

      <EventDetailsForm
        event={event}
        onChange={setEvent}
        coverImage={coverImage}
        coverImagePreview={coverImagePreview}
        onCoverImageChange={handleCoverImageChange}
      />

      <TicketTypesForm ticketTypes={ticketTypes} onChange={setTicketTypes} />

      <div className="flex justify-end space-x-4">
        <Button type="button" variant="outline">
          Save as Draft
        </Button>
        <Button type="submit">Create Event</Button>
      </div>
    </form>
  );
}
