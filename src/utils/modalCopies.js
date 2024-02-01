export function getRandomElement(array) {
  if (array.length === 0) {
    return "No records found";
  }

  const randomIndex = Math.floor(Math.random() * array.length);

  return array[randomIndex];
}
