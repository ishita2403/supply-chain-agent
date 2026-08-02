// frontend/src/components/EventSelector.jsx

export default function EventSelector({ events, selectedEventId, onSelect }) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <label>Select an event: </label>
      <select
        value={selectedEventId ?? ""}
        onChange={(e) => onSelect(Number(e.target.value))}
      >
        <option value="" disabled>-- choose an event --</option>
        {events.map((e) => (
          <option key={e.id} value={e.id}>
            #{e.id} [{e.event_type ?? "unclassified"}] {e.raw_text.slice(0, 60)}...
          </option>
        ))}
      </select>
    </div>
  );
}