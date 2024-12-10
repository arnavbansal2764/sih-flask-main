package main

import (
	"fmt"
	"os"

	"github.com/jpoz/groq"
)

func resumeBuilder(apiKey, resume, jobDescription string) (string, error) {
	var client *groq.Client

	if apiKey == "" {
		apiKey = os.Getenv("GROQ_API_KEY")
	}
	client = groq.NewClient(groq.WithAPIKey(apiKey))
	messages := []groq.Message{
		{
			Role:    "user",
			Content: fmt.Sprintf("Build a custom resume for this job posting. Here is the resume: %s and here is the job description: %s", resume, jobDescription),
		},
	}

	request := groq.CompletionCreateParams{
		Model:       "llama3-70b-8192",
		Messages:    messages,
		Temperature: 1,
		MaxTokens:   1024,
		TopP:        1,
	}

	response, err := client.CreateChatCompletion(request)
	if err != nil {
		return "", err
	}

	return response.Choices[0].Message.Content, nil
}
