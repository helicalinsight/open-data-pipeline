export default function getTimeStamp(timestamp = null) {
  let date;
  if (timestamp) {
    date = new Date(timestamp);
  } else {
    date = new Date();
  }
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear();

  let hours = date.getHours();
  let minutes = date.getMinutes();
  let ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12;
  hours = hours ? hours : 12;
  minutes = minutes < 10 ? "0" + minutes : minutes;
  
  let formattedDate = `${day}/${month}/${year}`;
  let strTime = hours + ":" + minutes + " " + ampm;

  return `${formattedDate} ${strTime}`;
}
