import { useState } from 'react';
import TrueNotionService from '../service/truenotion.service';

const useTrueNotion = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessages = async ({ message, history }) => {
    setLoading(true);
    const response = await TrueNotionService.sendToTrueNotion({ message, history });
    setMessages(prev => [
      ...prev,
      //{ role: 'user', parts: [{ text: message }] },
      { role: 'ai', parts: [{ text: response }] }
    ]);
    setLoading(false);
  };

  const updateMessage = (newMessages) => {
    setMessages(newMessages);
  };

  return { messages, loading, sendMessages, updateMessage };
};

export default useTrueNotion;