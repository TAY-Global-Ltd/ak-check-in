// Function to generate a random integer between min and max (inclusive)
function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export const students = [];

const studentsExample = [
  {
    event_id: "event-1",
    name: "Jack Sparrow",
    icon: "person_check",
    icon_type: "material",
    reward: "",
  },
  {
    event_id: "event-1",
    name: "Will Turner",
    icon: "person_check",
    icon_type: "material",
    reward: "",
  },
  {
    event_id: "event-0",
    name: "John Smith",
    icon: "person_check",
    icon_type: "material",
    reward: "⭐",
  },
  {
    event_id: "event-1",
    name: "Peter Parker",
    icon: "person_check",
    icon_type: "material",
    reward: "",
  },
  {
    event_id: "event-0",
    name: "Uzumaki Naruto",
    icon: "person",
    icon_type: "material",
    reward: "",
  },
];

students.push(...studentsExample);

const remainingObjectsCount = 40 - studentsExample.length;

for (let i = 0; i < remainingObjectsCount; i++) {
  const eventId = getRandomInt(0, 1) === 0 ? "event-0" : "event-1";

  const newObj = {
    event_id: eventId,
    name: `User ${i + studentsExample.length + 1}`,
    icon: "person_check",
    icon_type: "material",
    reward: "",
  };

  students.push(newObj);
}
