export function getTextColour(colour: string | undefined): string {
    if (typeof colour !== 'string') {
      return "black";
    }
    console.log(colour)
    const c = colour ?? "#FFFFFF";
    const hex = c.replace("#", "");
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    return brightness < 128 ? "white" : "black";
  }
  