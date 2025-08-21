export interface VenueData {
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

export interface EventData {
  title: string;
  slug: string;
  description: string;
  start_time: string;
  end_time: string;
  status: "draft" | "published" | "cancelled";
  capacity: number;
  cover_image_url: string;
}

export interface TicketType {
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
