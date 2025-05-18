/* eslint-disable no-unused-vars */
import { useEffect, useRef, useState } from "react";
import { InputGroup, Box, InputRightElement, Button } from "@chakra-ui/react";
import { motion } from "framer-motion";
import { Text } from "@chakra-ui/react";
import { Textarea } from "@chakra-ui/react";
import { DeleteIcon } from "@chakra-ui/icons";
import { ArrowForwardIcon } from "@chakra-ui/icons";
import ReactMarkdown from "react-markdown";
import useTrueNotion from "../hooks/useTrueNotion";
import trueNotionLogo from "../icons/truenotion.png";
import { Typewriter } from "react-simple-typewriter";
import GlobalSpotlightEffect from "./GlobalSpotlightEffect"; // import the spotlight effect

const ChatWithTrueNotion = () => {
  const { messages, loading, sendMessages, updateMessage } = useTrueNotion();
  const [input, setInput] = useState("");

  const AlwaysScrollToBottom = () => {
    const elementRef = useRef();
    useEffect(
      () =>
        elementRef.current.scrollIntoView({
          behavior: "smooth",
          block: "start",
          inline: "nearest",
        }),
      []
    );
    return <div ref={elementRef} />;
  };

  const handleSend = async () => {
    if (!input) return;
    // Scroll to top when Send button is clicked
    window.scrollTo({ top: 0, behavior: "smooth" });
    setInput("");
    updateMessage([
      ...messages,
      { role: "user", parts: [{ text: input }] },
    ]);
    sendMessages({ message: input, history: messages });
  };

  return (
    <>
      {/* Add the Global Spotlight effect component */}
      <GlobalSpotlightEffect />

      {/* Your existing chat interface */}
      <Box
        className={`w-[100%] self-center max-w-[1400px] m-6 rounded-md h-[80%] items-center ${
          messages.length === 0 ? "overflow-hidden" : "overflow-auto"
        }`}
        sx={{
          "&::-webkit-scrollbar": {
            width: "8px",
          },
          "&::-webkit-scrollbar-track": {
            background: "white",
          },
          "&::-webkit-scrollbar-thumb": {
            backgroundColor: "rgba(100, 100, 255, 0.5)",
            borderRadius: "3px",
          },
        }}
      >
        <Box className="overflow-auto px-16 py-6 flex flex-col gap-4">
          {messages.length > 0 ? (
            messages.map((message, index) => (
              <RenderMessage
                loading={loading}
                key={index + message.role}
                messageLength={messages.length}
                message={message}
                msgIndex={index}
              />
            ))
          ) : (
            <Introduction />
          )}
        </Box>
      </Box>

      {/* Input section */}
      <Box className="flex max-w-[1400px] px-16 pt-4 w-[100%] self-center">
        <Box className="flex w-[100%] gap-4 justify-between items-center">
          <Textarea
            placeholder="Ask me anything.."
            value={input || ""}
            rounded="2xl"
            sx={{
              resize: "none",
              padding: "16px 20px",
              background: "gray.700",
              color: "white",
              _placeholder: { color: "white" },
              fontSize: "lg",
              minHeight: "3.5rem",
            }}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            variant={"unstyled"}
          />
          <Box className="flex gap-3 flex-row">
            <Button
              rounded="2xl"
              bg="green.500"
              color="white"
              _hover={{ bg: "green.600" }}
              variant="solid"
              h="3rem"
              fontSize="lg"
              onClick={handleSend}
              rightIcon={<ArrowForwardIcon boxSize={6} />}
            >
              Send
            </Button>
            <Button
              rounded="2xl"
              color={"white"}
              _hover={{ bg: "blue.500" }}
              variant={"outline"}
              h="3rem"
              fontSize="lg"
              onClick={() => updateMessage([])}
              rightIcon={<DeleteIcon boxSize={6} />}
            >
              Clear
            </Button>
          </Box>
        </Box>
      </Box>
    </>
  );
};

const Introduction = () => {
  const [showSecondTypewriter, setShowSecondTypewriter] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowSecondTypewriter(true), 14500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Box className="flex flex-col items-center justify-center h-screen text-center px-8">
      {/* Logo + Heading on the same line */}
      <Box className="flex items-center justify-center gap-8 mb-6">
        <img
          src={trueNotionLogo}
          alt="TrueNotion Logo"
          style={{ width: "120px", height: "120px" }}
        />
        <Text
          fontSize="8xl"
          bgGradient="linear(to-r, white, blue.300)"
          bgClip="text"
          color="transparent"
          fontWeight="bold"
        >
          <span style={{ fontWeight: "bold" }}>True</span>
          <span style={{ fontWeight: "normal" }}>Notion AI</span>
        </Text>
      </Box>

      {/* Rest of the text is stacked vertically */}
      <Text
        fontSize="3xl"
        fontWeight="bold"
        bgGradient="linear(to-r, white, blue.300)"
        bgClip="text"
        color="transparent"
        mt={6}
      >
        <Typewriter
          words={[
            "👾 Agentic RAG with User Defined Context",
            "✨ Fully Customizable Crew AI Agent",
            "♻️ Instant Sync with Notion Database",
          ]}
          loop={1}
          cursor
          cursorStyle="|"
          typeSpeed={50}
          deleteSpeed={20}
          delaySpeed={2000}
        />
      </Text>

      {showSecondTypewriter && (
        <Text
          fontSize="2xl"
          bgGradient="linear(to-r, white, blue.300)"
          bgClip="text"
          color="gray"
          mt={4}
        >
          <Typewriter
            words={["Type your query below.. 🡻"]}
            loop={1}
            cursor
            cursorStyle="|"
            typeSpeed={50}
            deleteSpeed={20}
            delaySpeed={2000}
          />
        </Text>
      )}
    </Box>
  );
};

const RenderMessage = ({ message, msgIndex, loading, messageLength }) => {
  const { parts, role } = message;

  const Loader = () =>
    msgIndex === messageLength - 1 &&
    loading && (
      <Box className="flex self-start pt-4 gap-2">
        <Box
          bgColor={"white"}
          className="dot w-3 h-3 rounded-full animate-bounce"
        />
        <Box
          bgColor={"white"}
          className="dot w-3 h-3 rounded-full animate-bounce delay-200"
        />
        <Box
          bgColor={"white"}
          className="dot w-3 h-3 rounded-full animate-bounce delay-400"
        />
      </Box>
    );

  return parts.map((part, index) =>
    part.text ? (
      <>
        <Box
          as={motion.div}
          className={`flex overflow-auto max-w-[95%] md:max-w-[96%] w-fit items-end my-3 p-2 px-4 rounded-2xl ${
            role === "user" ? "self-end" : "self-start"
          }`}
          bgColor={role === "user" ? "green.500" : "gray.200"}
          textColor={role === "user" ? "white" : "black"}
          initial={{ opacity: 0, scale: 0.5, y: 20, x: role === "user" ? 20 : -20 }}
          animate={{ opacity: 1, scale: 1, y: 0, x: 0 }}
          key={index}
        >
          <ReactMarkdown
            className="text-lg"
            key={index + part.text}
            components={{
              p: ({ node, ...props }) => <Text {...props} className="text-lg" />,
              code: ({ node, ...props }) => (
                <pre
                  {...props}
                  className="text-base font-mono text-white bg-slate-800 rounded-md p-4 overflow-auto m-3"
                />
              ),
            }}
          >
            {part.text}
          </ReactMarkdown>
        </Box>  
        <Loader />
      </>
    ) : (
      <Loader key={index + part.text} />
    )
  );
};

export default ChatWithTrueNotion;
