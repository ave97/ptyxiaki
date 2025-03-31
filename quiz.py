class Question:
    def __init__(
        self,
        questionNum: int,
        questionText: str,
        option1: str,
        option2: str,
        option3: str,
        option4: str,
        correctAnswer: str,
    ):
        self.questionNum = questionNum
        self.questionText = questionText
        self.option1 = option1
        self.option2 = option2
        self.option3 = option3
        self.option4 = option4
        self.correctAnswer = correctAnswer

    def getQuestionNum(self):
        return self.questionNum

    def getQuestionText(self):
        return self.questionText

    def getOption1(self):
        return self.option1

    def getOption2(self):
        return self.option2

    def getOption3(self):
        return self.option3

    def getOption4(self):
        return self.option4
    
    def getCorrectAnswer(self):
        return self.correctAnswer


class Quiz:
    def __init__(
        self, quizTitle: str, quizTime: int, quizDescription: str
    ):  # μπορω να προσθεσω created_by: str και created_at):
        self.quizTitle = quizTitle
        self.quizTime = quizTime
        self.quizDescription = quizDescription
        # self.created_by = created_by
        # self.created_at = created_at

    def getTitle(self):
        return self.quizTitle

    def getTime(self):
        return self.quizTime

    def getDescription(self):
        return self.quizDescription

    # def getCreatedBy(self):
    #     return self.created_by

    # def getCreatedAt(self):
    #     return self.created_at

    def print(self):
        print(
            f"Quiz title: {self.quizTitle}, time(sec): {self.quizTime}, quiz description: {self.quizDescription}"
        )
