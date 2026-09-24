export default function EventSelector({ events, selectedEventId, onSelect }) {
  const getEventLabel = (event) => {
    const text = event.raw_text.toLowerCase();

    if (event.event_type === "supplier_delay") {
      const supplier = event.raw_text.split(" reports")[0];
      const delayMatch = event.raw_text.match(/(\d+)-day delay/i);
      const componentMatch = event.raw_text.match(
        /on (.*?) shipment/i
      );

      const delay = delayMatch ? delayMatch[1] : "";
      const component = componentMatch ? componentMatch[1] : "";

      return `#${event.id} — ${supplier} — ${delay}-day delay — ${component}`;
    }

    if (event.event_type === "quality_issue") {
      const defectMatch = event.raw_text.match(/(\d+)% defect rate/i);
      const componentMatch = event.raw_text.match(
        /on (.*?) batch/i
      );

      const defect = defectMatch ? defectMatch[1] : "";
      const component = componentMatch ? componentMatch[1] : "";

      return `#${event.id} — Quality Inspection — ${defect}% defect — ${component}`;
    }

    if (text.includes("on-time delivery")) {
      const supplier = event.raw_text.split(" confirms")[0];

      return `#${event.id} — ${supplier} — On-time delivery`;
    }

    return `#${event.id} — ${event.event_type ?? "Unclassified"}`;
  };

  return (
    <div style={{ marginBottom: "1rem" }}>
      <label>Select an event: </label>

      <select
        value={selectedEventId ?? ""}
        onChange={(e) => onSelect(Number(e.target.value))}
      >
        <option value="" disabled>
          -- choose an event --
        </option>

        {events.map((event) => (
          <option key={event.id} value={event.id}>
            {getEventLabel(event)}
          </option>
        ))}
      </select>
    </div>
  );
}