from app.services.condition.enums import ConditionOperatorEnum


class ConditionEvaluator:
    """
    Проверяет выполнение условия для извлечённого значения.
    """

    def __init__(self, operator: ConditionOperatorEnum, target_value: str):
        self.operator = operator
        self.target_value = target_value

    def check(self, actual_value: str) -> bool:
        if self.operator == ConditionOperatorEnum.EQUALS:
            return actual_value == self.target_value

        if self.operator == ConditionOperatorEnum.CONTAINS:
            return self.target_value in actual_value

        if self.operator == ConditionOperatorEnum.GREATER_THAN:
            return float(actual_value) > float(self.target_value)

        if self.operator == ConditionOperatorEnum.LESS_THAN:
            return float(actual_value) < float(self.target_value)

        raise ValueError(f"Unsupported operator: {self.operator}")
    
    @staticmethod
    def check_condition(condition: str, actual_value: str) -> bool:
        try:
            operator_str, target_value = condition.split(":", 1)
            operator = ConditionOperatorEnum[operator_str]
        except Exception as e:
            raise ValueError(f"Неверный формат condition: {condition}") from e

        evaluator = ConditionEvaluator(operator, target_value)
        return evaluator.check(actual_value)
        
    def __repr__(self):
        return (
            f"ConditionEvaluator("
            f"operator='{self.operator.value}', "
            f"target_value='{self.target_value}')"
        )
