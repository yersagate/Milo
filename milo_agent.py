# milo_agent.py
import time

class MiloAgent:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def run_autonomous_task(self, objective: str):
        """Executes a multi-step autonomous task with planning and self-correction."""
        print(f"[*] Autonomous Agent initialized for objective: '{objective}'")

        # Step 1: Planning
        print("[1/3] Planning steps...")
        plan_prompt = f"Break down this objective into 3 concrete steps: {objective}"
        plan = self._call_model(plan_prompt)
        print(f"Plan:\n{plan}\n")

        # Step 2: Execution (Coder role)
        print("[2/3] Executing solution (Coder role)...")
        exec_prompt = f"Based on this plan:\n{plan}\nWrite the solution/code for: {objective}"
        solution = self._call_model(exec_prompt)
        print(f"Solution generated.\n")

        # Step 3: Review (Reviewer role)
        print("[3/3] Reviewing and testing (Reviewer role)...")
        review_prompt = f"Review this solution for bugs, security issues, or improvements:\n{solution}"
        review = self._call_model(review_prompt)
        print(f"Review & Feedback:\n{review}\n")

        return {
            "objective": objective,
            "plan": plan,
            "solution": solution,
            "review": review
        }

    def _call_model(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
