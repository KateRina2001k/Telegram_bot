from aiogram.dispatcher.filters.state import State, StatesGrade


class NewsStates(StatesGrade):
    title = State()
    content = State()
    image = State()

class CreateGradeStates(StatesGrade):
    grade_name = State()


class StartStates(StatesGrade):
    grade_name = State()


class SelectDistributionStates(StatesGrade):
    name2_profile = State()


class CreateDistributionStates(StatesGrade):
    name2_profile = State()


class SelectGradeStates(StatesGrade):
    grade_name = State()


class ScheduleStates(StatesGrade):
    select_grade = State()
    image = State()


class AskQuestionStates(StatesGrade):
    get_question = State()


class AnswerTheQuestion(StatesGrade):
    start = State()
    answer = State()