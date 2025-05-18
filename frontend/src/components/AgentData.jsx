import React, { useState } from 'react';
import { Box, Textarea, FormControl, FormLabel, Button, Flex } from '@chakra-ui/react';

const defaultPlaceholders = {
  agentName: 'Data Analyst',
  role: 'Expert in giving Strictly Data-driven Answers',
  goal: "Answer user questions by analyzing available textual data, relying strictly on verified content.",
  backstory:
    "You are a trusted expert in data analysis, responsible for extracting insights and answering queries using a diverse range of unstructured text documents like resumes, schedules, research notes, travel plans, and more. You must only use the data that is available, avoid assumptions based on foreign data, and explicitly state if information is inferred or missing.",
  taskDescription: `You are given a user question: '{user_question}' and a collection of unstructured documents below:

{context}

Before starting the main analysis, check if the user question is a general conversational message (like 'hi', 'hello', 'how are you', etc.). If so, respond briefly and politely without analyzing any documents. 

Otherwise, analyze all available documents and determine which of the following analysis steps are needed to answer the query effectively. You may perform **one, several, or all** of these based on relevance:

Mark inferred events as **'(inferred)'**, and cite the document sources when possible.

1. **Question Answering:** If the answer appears directly in the documents, retrieve it. If you can infer it with high confidence, mark it as (inferred).
2. **Data Extraction:** Extract and list relevant entities such as names, dates, organizations, locations, roles, relationships, or timelines to help clarify or support your answer. Use 'Not available' or 'Unclear' where data is missing.
3. **Contextual Inference:** If the answer isn't explicitly stated but can be logically deduced (e.g., availability, intent), infer it using document clues. Clearly mark such answers as **'(inferred)'**. Never guess beyond what the documents justify.
4. **Document Classification:** If needed, classify each document into categories like names, lists, portfolio, biodata, companies or any specific group. This may help you route and prioritize relevant information.
`,
  expected_output:
    "A well-structured, data-backed answer based on provided content. If the answer requires a date or time, first analyze the events with respect to today's date and time: {timestamp}, and ensure that the date or time is not in the past (e.g., for planning, schedules, events, or trips). Do not consider past events when the question is about future planning. Clearly indicate anything inferred with '(inferred)' or explicitly state when no data is available.",
};

const labels = {
  agentName: 'Agent Name',
  role: 'Role',
  goal: 'Goal',
  backstory: 'Backstory',
  taskDescription: 'Task Description',
  expected_output: 'Expected Output',
};

const AgentConfigForm = () => {
  const [form, setForm] = useState({
    agentName: '',
    role: '',
    goal: '',
    backstory: '',
    taskDescription: '',
    expectedOutput: '',
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async () => {
    const jsonData = {
      agent: {
        name: form.agentName || defaultPlaceholders.agentName,
        role: form.role || defaultPlaceholders.role,
        goal: form.goal || defaultPlaceholders.goal,
        backstory: form.backstory || defaultPlaceholders.backstory,
      },
      task: {
        description: form.taskDescription || defaultPlaceholders.taskDescription,
        expected_output: form.expectedOutput || defaultPlaceholders.expected_output,
      },
    };

    try {
      const response = await fetch("http://localhost:8000/save-agent-config", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonData),
      });

      if (response.ok) {
        // Refresh the webpage after a successful save
        window.location.reload();
      } else {
        console.error("Error saving configuration.");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  // Base style for all text fields
  const baseTextareaStyle = {
    rounded: "2xl",
    sx: {
      resize: "none",
      padding: "16px 20px",
      background: "gray.700",
      color: "white",
      _placeholder: { color: "white" },
      fontSize: "lg",
    },
    variant: "unstyled",
  };

  return (
    <Box p={4} w="full">
      {/* Responsive Flex container maintains exactly the same layout */}
      <Flex direction={{ base: "column", md: "row" }} gap={6} flexGrow={1}>
        {/* Column 1: Agent Name, Role, Goal */}
        <Box w={{ base: "100%", md: "25%" }} minHeight={{ base: "auto", md: "30rem" }}>
          {['agentName', 'role', 'goal'].map((field) => (
            <FormControl key={field} mb={4}>
              <FormLabel>{labels[field]}</FormLabel>
              <Textarea
                name={field}
                value={form[field]}
                onChange={handleChange}
                placeholder={defaultPlaceholders[field]}
                {...baseTextareaStyle}
                minHeight="6rem"
              />
            </FormControl>
          ))}
        </Box>

        {/* Column 2: Backstory */}
        <Box flex="1" w={{ base: "100%", md: "auto" }}>
          <FormControl mb={4}>
            <FormLabel>{labels.backstory}</FormLabel>
            <Textarea
              name="backstory"
              value={form.backstory}
              onChange={handleChange}
              placeholder={defaultPlaceholders.backstory}
              {...baseTextareaStyle}
              minHeight="25rem"
            />
          </FormControl>
        </Box>

        {/* Column 3: Task Description */}
        <Box flex="1" w={{ base: "100%", md: "auto" }}>
          <FormControl mb={4}>
            <FormLabel>{labels.taskDescription}</FormLabel>
            <Textarea
              name="taskDescription"
              value={form.taskDescription}
              onChange={handleChange}
              placeholder={defaultPlaceholders.taskDescription}
              {...baseTextareaStyle}
              minHeight="25rem"
            />
          </FormControl>
        </Box>

        {/* Column 4: Expected Output */}
        <Box flex="1" w={{ base: "100%", md: "auto" }}>
          <FormControl mb={4}>
            <FormLabel>{labels.expected_output}</FormLabel>
            <Textarea
              name="expectedOutput"
              value={form.expectedOutput}
              onChange={handleChange}
              placeholder={defaultPlaceholders.expected_output}
              {...baseTextareaStyle}
              minHeight="25rem"
            />
          </FormControl>
        </Box>
      </Flex>

      {/* Save button */}
      <Box textAlign="center" mt={4} minHeight={{ base: "auto", md: "5rem" }}>
        <Button rounded="2xl" colorScheme="green" onClick={handleSubmit}>
          Save & Reload
        </Button>
      </Box>
    </Box>
  );
};

export default AgentConfigForm;
