import { DOMAIN } from "./backend_domain";

const BACKEND_URL = DOMAIN+'/chat'; 

const sendToTrueNotion = async ({ message, history }) => {
  try {
    const response = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question: message,
        history: history.map(m => [m.parts[0].text, ""])  // optionally adapt if needed
      })
    });

    const data = await response.json();
    return data.answer;
  } catch (error) {
    console.error("Error communicating with TrueNotion backend:", error);
    return "Sorry, I couldn’t connect to the backend.. Please try again after sometime :(";
  }
};

export default { sendToTrueNotion };
