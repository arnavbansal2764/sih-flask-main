package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/jpoz/groq"
)

type InterviewAssistant struct {
	apiKey string
	client *groq.Client
	resume string
}

func NewInterviewAssistant(apiKey, pdfPath string) (*InterviewAssistant, error) {
	if apiKey == "" {
		apiKey = os.Getenv("GROQ_API_KEY")
	}

	client := groq.NewClient(groq.WithAPIKey(apiKey))

	assistant := &InterviewAssistant{
		apiKey: apiKey,
		client: client,
	}

	if pdfPath != "" {
		resume, err := assistant.extractTextFromPDF(pdfPath)
		if err != nil {
			return nil, err
		}
		assistant.resume = resume
	} else {
		assistant.resume = ""
	}

	return assistant, nil
}

func (ia *InterviewAssistant) extractTextFromPDF(pdfPath string) (string, error) {
	content, err := os.ReadFile(pdfPath)
	if err != nil {
		return "", err
	}

	// Use a PDF parsing library to extract text from the PDF content
	// For example, using github.com/ledongthuc/pdf
	// Replace this with actual implementation
	text := string(content) // Placeholder for extracted text

	return text, nil
}

func (ia *InterviewAssistant) generateQuestions() ([]string, error) {
	prompt := fmt.Sprintf("Generate 5-10 concise and formal technical questions based on the following resume: %s", ia.resume)

	messages := []groq.Message{
		{
			Role:    "system",
			Content: "You are an interviewer who asks only formal and concise questions.",
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

	chatCompletion, err := ia.client.CreateChatCompletion(request)
	if err != nil {
		return nil, err
	}

	content := chatCompletion.Choices[0].Message.Content
	questions := strings.Split(strings.TrimSpace(content), "\n")

	return questions, nil
}

// func main() {
//     // Example usage
//     apiKey := "" // or get from environment variables
//     pdfPath := "resume.pdf"

//     assistant, err := NewInterviewAssistant(apiKey, pdfPath)
//     if err != nil {
//         fmt.Println("Error creating assistant:", err)
//         return
//     }

//     questions, err := assistant.generateQuestions()
//     if err != nil {
//         fmt.Println("Error generating questions:", err)
//         return
//     }

//     for _, question := range questions {
//         fmt.Println(question)
//     }
// }
