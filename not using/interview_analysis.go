package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/jpoz/groq"
)

func analyzeResponse(question, transcript string, apiKey string) (string, error) {
	if apiKey == "" {
		apiKey = os.Getenv("GROQ_API_KEY")
	}

	client := groq.NewClient(groq.WithAPIKey(apiKey))
	prompt := fmt.Sprintf("Based on the question: '%s', evaluate the response: '%s' and provide constructive feedback.", question, transcript)

	messages := []groq.Message{
		{
			Role:    "system",
			Content: "You are an evaluator who gives constructive feedback on interview responses.",
		},
		{
			Role:    "user",
			Content: prompt,
		},
	}

	request := groq.CompletionCreateParams{
		Model:     "llama3-8b-8192",
		Messages:  messages,
		MaxTokens: 150,
	}

	chatCompletion, err := client.CreateChatCompletion(request)
	if err != nil {
		return "", err
	}

	feedback := strings.TrimSpace(chatCompletion.Choices[0].Message.Content)
	return feedback, nil
}
