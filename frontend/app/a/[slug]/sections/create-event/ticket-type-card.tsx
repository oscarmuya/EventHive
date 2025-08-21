"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Trash2 } from "lucide-react";
import { TicketType } from "./types";

interface TicketTypeCardProps {
  ticket: TicketType;
  index: number;
  canRemove: boolean;
  onChange: (field: keyof TicketType, value: any) => void;
  onRemove: () => void;
}

export function TicketTypeCard({
  ticket,
  index,
  canRemove,
  onChange,
  onRemove,
}: TicketTypeCardProps) {
  return (
    <div className="border rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-medium">Ticket Type {index + 1}</h4>
        {canRemove && (
          <Button
            type="button"
            variant="destructive"
            size="sm"
            onClick={onRemove}
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
            onChange={(e) => onChange("name", e.target.value)}
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
            onChange={(e) => onChange("price", parseFloat(e.target.value) || 0)}
            placeholder="0.00"
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label>Description</Label>
        <Textarea
          value={ticket.description}
          onChange={(e) => onChange("description", e.target.value)}
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
              onChange("quantity_total", parseInt(e.target.value) || 0)
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
              onChange("quantity_sold", parseInt(e.target.value) || 0)
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
              onChange("per_person_limit", parseInt(e.target.value) || 1)
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
            onChange={(e) => onChange("sales_start", e.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label>Sales End Date & Time *</Label>
          <Input
            type="datetime-local"
            value={ticket.sales_end}
            onChange={(e) => onChange("sales_end", e.target.value)}
            required
          />
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id={`active-${ticket.id}`}
          checked={ticket.is_active}
          onChange={(e) => onChange("is_active", e.target.checked)}
          className="rounded border-gray-300"
        />
        <Label htmlFor={`active-${ticket.id}`}>
          Active (available for sale)
        </Label>
      </div>
    </div>
  );
}
