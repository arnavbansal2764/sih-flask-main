package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"

	"github.com/jpoz/groq"
	"github.com/redis/go-redis/v9"
)

var ctx = context.Background()

type Message struct {
	Type string      `json:"type"`
	Data interface{} `json:"data"`
}

type Response struct {
	ClientID string  `json:"clientId"`
	Message  Message `json:"message"`
}

func downloadPDF(url, savePath string) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return err
		}
		return os.WriteFile(savePath, body, 0644)
	}
	return fmt.Errorf("failed to download PDF, status code: %d", resp.StatusCode)
}

func pdfToText(pdfPath string) (string, error) {
	// Implement PDF to text conversion here
	// Placeholder for actual implementation
	content, err := os.ReadFile(pdfPath)
	if err != nil {
		return "", err
	}
	return string(content), nil
}

func getBotResponse(apiKey, userInput, resumeText string) (string, error) {
	var client *groq.Client

	if apiKey == "" {
		apiKey = os.Getenv("GROQ_API_KEY")
	}
	client = groq.NewClient(groq.WithAPIKey(apiKey))
	messages := []groq.Message{
		{
			Role:    "system",
			Content: "You Are A Profile Analyser Analyse The Interviews Profile Professionally",
		},
		{
			Role:    "user",
			Content: fmt.Sprintf("Respond to this prompt %s using this data %s", userInput, resumeText),
		},
	}

	request := groq.CompletionCreateParams{
		Model:     "llama3-8b-8192",
		Messages:  messages,
		MaxTokens: 1000,
	}

	response, err := client.CreateChatCompletion(request)
	if err != nil {
		return "", err
	}

	return response.Choices[0].Message.Content, nil
}

func generateRecommendation(apiKey, resumeText, jobDescription string) (string, error) {
	query := fmt.Sprintf(`
Job Description:

You will critically and in a high level analyze a job seeker's profile based on the following job description and evaluate it across several key parameters. Provide an overall rating out of 100, considering the alignment of the job seeker’s profile which is given to you with the job description. The parameters you should consider are: Skills Match, Experience, Education, Accomplishments, Cultural Fit, Geographical Fit, Career Progression, Availability, Industry Knowledge, and Recommendations/References.

---

Job Description:

%s
---
Instructions:

1. Skills Match (0-20 points):
- Evaluate how well the job seeker's technical and soft skills align with the job requirements.

2. Experience (0-20 points):
- Consider the relevance of the job seeker's years of experience, prior roles, and industry experience to the job description.

3. Education (0-10 points):
- Assess the relevance of the job seeker’s educational background, including degrees and certifications, to the job requirements.

4. Accomplishments (0-10 points):
- Evaluate the significance of the job seeker's professional achievements and project experience in relation to the job description.

5. Cultural Fit (0-10 points):
- Determine how well the job seeker’s values and adaptability align with the company’s culture and work environment.

6. Geographical Fit (0-5 points):
- Consider the job seeker’s location in relation to the job location and their willingness to relocate, if necessary.

7. Career Progression (0-10 points):
- Evaluate the job seeker’s career growth trajectory and their ability to take on increasing responsibilities.

8. Availability (0-5 points):
- Assess the job seeker’s availability to start work and their willingness to commit to the company.

9. Industry Knowledge (0-5 points):
- Evaluate the job seeker’s understanding of industry trends and market conditions, and their ability to contribute valuable insights.

10. Recommendations/References (0-5 points):
- Assess the quality and relevance of the job seeker’s recommendations or references.

---
Output format:

Overall Rating: [Sum of all points out of 100]

Strengths:
- [Strength 1]
- [Strength 2]
- ...

Weaknesses:
- [Weakness 1]
- [Weakness 2]
- ...

Overall Assessment:
[Provide a brief summary of the job seeker’s strengths and weaknesses in relation to the job description, highlighting the key factors that influenced the overall rating.]
`, jobDescription)

	return getBotResponse(apiKey, query, resumeText)
}

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

func main() {
	apiKey := "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"

	// redisClient := redis.NewClient(&redis.Options{
	// 	Addr: "localhost:6379",
	// 	DB:   0,
	// })
	redisClient := redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
		DB:   0,
	})
	fmt.Println("RUNNING: REDIS AI BACKEND (OTHERS)")

	for {
		responseStr, err := redisClient.RPop(ctx, "messages").Result()
		if err != nil {
			if err == redis.Nil {
				continue
			}
			fmt.Println(err)
			continue
		}

		var res Response
		err = json.Unmarshal([]byte(responseStr), &res)
		if err != nil {
			fmt.Println("Error unmarshaling response:", err)
			continue
		}

		clientId := res.ClientID
		message := res.Message
		msgType := message.Type
		dataMap, ok := message.Data.(map[string]interface{})
		if !ok {
			fmt.Println("Invalid data format")
			continue
		}

		dataJSON, _ := json.MarshalIndent(dataMap, "", "    ")
		fmt.Println(string(dataJSON))

		switch msgType {
		case "GET_RECOMMENDATION":
			jobDescription, _ := dataMap["job_description"].(string)
			resumeURL, _ := dataMap["resume"].(string)
			if resumeURL == "" || jobDescription == "" {
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Job Description and Resume Absent"}`)
				continue
			}
			pdfPath := "downloaded_resume.pdf"
			if err := downloadPDF(resumeURL, pdfPath); err != nil {
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Not able to download PDF"}`)
				continue
			}
			os.Remove(pdfPath)

			resumeText, err := pdfToText(pdfPath)
			if err != nil {
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Error extracting text from PDF"}`)
				continue
			}

			recommendation, err := generateRecommendation(apiKey, resumeText, jobDescription)
			if err != nil {
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Error generating recommendation"}`)
				continue
			}

			result := map[string]interface{}{
				"type": "RECOMMENDATION",
				"payload": map[string]interface{}{
					"recommendation": recommendation,
				},
			}
			jsonString, _ := json.Marshal(result)
			redisClient.Publish(ctx, clientId, string(jsonString))
		case "GET_RESUME_BUILD":
			println("GET_RESUME_BUILD")
			jobDescription, _ := dataMap["job_description"].(string)
			resumeURL, _ := dataMap["resume"].(string)
			if resumeURL == "" || jobDescription == "" {
				println("ERROR:1")
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Job Description and Resume Absent"}`)
				continue
			}
			pdfPath := "downloaded_resume.pdf"
			if err := downloadPDF(resumeURL, pdfPath); err != nil {
				println("ERROR:2")
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Not able to download PDF"}`)
				continue
			}
			os.Remove(pdfPath)

			resumeText, err := pdfToText(pdfPath)
			if err != nil {
				println("ERROR:3")
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Error extracting text from PDF"}`)
				continue
			}

			resumeBuilt, err := resumeBuilder(apiKey, resumeText, jobDescription)
			if err != nil {
				println("ERROR:4")
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Error building resume"}`)
				continue
			}

			result := map[string]interface{}{
				"type": "RESUME_BUILD",
				"payload": map[string]interface{}{
					"resume": resumeBuilt,
				},
			}
			fmt.Printf("Resume_Built: %s", resumeBuilt)
			jsonString, _ := json.Marshal(result)
			redisClient.Publish(ctx, clientId, string(jsonString))
		case "GET_QUESTIONS":
			resumeURL, _ := dataMap["resume"].(string)
			if resumeURL == "" {
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Resume Absent"}`)
				continue
			}
			pdfPath := "downloaded_resume.pdf"
			if err := downloadPDF(resumeURL, pdfPath); err != nil {
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Not able to download PDF"}`)
				continue
			}
			os.Remove(pdfPath)

			assistant, err := NewInterviewAssistant(apiKey, pdfPath)
			if err != nil {
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Error creating assistant"}`)
				continue
			}

			questions, err := assistant.generateQuestions()
			if err != nil {
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Error generating questions"}`)
				continue
			}

			result := map[string]interface{}{
				"type": "SIMILARITY_SCORE",
				"payload": map[string]interface{}{
					"questions": questions,
				},
			}
			jsonString, _ := json.Marshal(result)
			redisClient.Publish(ctx, clientId, string(jsonString))
			fmt.Println("published")
		case "GET_INTERVIEW_ANALYSIS":
			questionResponses, ok := dataMap["question_responses"].([]interface{})
			if !ok || questionResponses == nil {
				redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Question Responses Absent"}`)
				continue
			}

			var analysisResults []map[string]string

			for _, item := range questionResponses {
				itemMap, _ := item.(map[string]interface{})
				question, _ := itemMap["question"].(string)
				transcript, _ := itemMap["transcript"].(string)

				if question == "" || transcript == "" {
					continue
				}

				feedback, err := analyzeResponse(question, transcript, apiKey)
				if err != nil {
					continue
				}

				analysisResult := map[string]string{
					"question":   question,
					"transcript": transcript,
					"feedback":   feedback,
				}
				analysisResults = append(analysisResults, analysisResult)
			}

			analysisResultJSON, _ := json.Marshal(analysisResults)
			result := map[string]interface{}{
				"type": "INTERVIEW_ANALYSIS",
				"payload": map[string]interface{}{
					"analysis": string(analysisResultJSON),
				},
			}
			jsonString, _ := json.Marshal(result)
			redisClient.Publish(ctx, clientId, string(jsonString))
			fmt.Println("published")
		default:
			redisClient.Publish(ctx, clientId, `{"type": "ERROR", "message": "Unknown message type"}`)
		}
	}
}
