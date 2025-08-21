"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Plus } from "lucide-react";
import { TicketType } from "./types";
import { TicketTypeCard } from "./ticket-type-card";

interface TicketTypesFormProps {
  ticketTypes: TicketType[];
  onChange: (ticketTypes: TicketType[]) => void;
}

export function TicketTypesForm({
  ticketTypes,
  onChange,
}: TicketTypesFormProps) {
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
    onChange([...ticketTypes, newTicket]);
  };

  const removeTicketType = (id: string) => {
    onChange(ticketTypes.filter((ticket) => ticket.id !== id));
  };

  const updateTicketType = (
    id: string,
    field: keyof TicketType,
    value: any
  ) => {
    onChange(
      ticketTypes.map((ticket) =>
        ticket.id === id ? { ...ticket, [field]: value } : ticket
      )
    );
  };

  return (
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
          <TicketTypeCard
            key={ticket.id}
            ticket={ticket}
            index={index}
            canRemove={ticketTypes.length > 1}
            onChange={(field, value) =>
              updateTicketType(ticket.id, field, value)
            }
            onRemove={() => removeTicketType(ticket.id)}
          />
        ))}
      </CardContent>
    </Card>
  );
}
