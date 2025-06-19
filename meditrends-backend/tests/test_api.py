### MediTrends API Testing
### Use this file in VS Code with REST Client extension to test your API

### 1. Health Check - Test if API is running
GET http://localhost:5000/api/health

###

### 2. Basic Search - Simple query
GET http://localhost:5000/api/search?q=headache from computer screen

###

### 3. Search with Parameters - More specific search
GET http://localhost:5000/api/search?q=back pain after gym&sort=top&time_filter=month&limit=20

###

### 4. Search with Display Format - Formatted for frontend
GET http://localhost:5000/api/search?q=anxiety depression&sort=relevance&limit=15&format=display

###

### 5. Medical Condition Search
GET http://localhost:5000/api/search?q=diabetes symptoms&sort=relevance&time_filter=year&limit=25

###

### 6. Pain-Related Search
GET http://localhost:5000/api/search?q=chronic pain management&sort=top&time_filter=all&limit=30

###

### 7. Mental Health Search
GET http://localhost:5000/api/search?q=help with anxiety attacks&sort=relevance&limit=20

###

### 8. Medication Side Effects Search
GET http://localhost:5000/api/search?q=ibuprofen side effects&sort=top&time_filter=year&limit=15

###

### 9. Fitness Injury Search
GET http://localhost:5000/api/search?q=shoulder pain weightlifting&sort=relevance&limit=20

###

### 10. Sleep Problems Search
GET http://localhost:5000/api/search?q=insomnia cant sleep&sort=top&time_filter=month&limit=25

###

### 11. POST Request - Alternative method
POST http://localhost:5000/api/search
Content-Type: application/json

{
  "q": "migraine triggers",
  "sort": "relevance",
  "time_filter": "month",
  "limit": 20,
  "format": "display"
}

###

### 12. Search Suggestions
GET http://localhost:5000/api/suggestions?q=head

###

### 13. Search Suggestions - Partial medication
GET http://localhost:5000/api/suggestions?q=ibu

###

### 14. Get Subreddit Categories
GET http://localhost:5000/api/subreddits

###

### 15. Get Specific Subreddit Category
GET http://localhost:5000/api/subreddits?category=medical_primary

###

### 16. Get Pain Management Subreddits
GET http://localhost:5000/api/subreddits?category=pain_management&limit=10

###

### 17. API Statistics
GET http://localhost:5000/api/stats

###

### 18. Test Error Handling - Empty query
GET http://localhost:5000/api/search?q=

###

### 19. Test Error Handling - Invalid sort parameter
GET http://localhost:5000/api/search?q=test&sort=invalid

###

### 20. Test Error Handling - Large limit
GET http://localhost:5000/api/search?q=test&limit=9999

###

### 21. Complex Medical Query
GET http://localhost:5000/api/search?q=Type 2 diabetes medication side effects metformin&sort=top&time_filter=year&limit=30

###

### 22. Work-Related Health Query
GET http://localhost:5000/api/search?q=carpal tunnel syndrome programming&sort=relevance&limit=20