export const destinations = Object.freeze([
  "home", "play", "collection", "multiplayer", "watch", "settings"
]);

export function navigate(current, destination) {
  if (!destinations.includes(destination))
    throw new Error("Unknown destination: " + destination);
  return {
    previous: current,
    current: destination,
    direction: destination === "home" ? "back" : "forward"
  };
}

export function updateSetting(state, key, value) {
  return { ...state, [key]: value };
}

export function layoutFor(width) {
  if (!Number.isFinite(width) || width <= 0)
    throw new Error("Invalid viewport width");
  return width < 600 ? "compact" :
         width < 1024 ? "medium" : "wide";
}
