import sys

from crossword import *


class Creator():

    def __init__(self, crossword, heuristic):
        '''
        initializes new crossword to inherit from crossword class
        also initializes domain for each variable
        '''
        self.crossword = crossword
        self.heuristic = heuristic
        self.domains = {}
        for var in self.crossword.variables:
            self.domains[var] = self.crossword.words.copy()

    def is_domain_consistent(self):
        """
        Enforce node consistency:
        Remove words from each domain that do not satisfy unary constraints.
        In this problem, the only unary constraint is: word length == variable length.
        """
        for var in self.domains:
            to_remove = set()
            for word in self.domains[var]:
                if len(word) != var.length:
                    to_remove.add(word)

            # حذف موارد ناسازگار
            self.domains[var] -= to_remove




    def revise(self, x, y):
        """
        Make domain[x] arc-consistent with y.
        Remove values from domain[x] that have no possible match in domain[y].
        Returns True if a revision was made (values removed), else False.
        """

        revised = False

        # اگر تلاقی ندارند، هیچ کاری نمی‌کنیم
        overlap = self.crossword.overlaps[(x, y)]
        if overlap is None:
            return False

        i, j = overlap  # موقعیت حروف مشترک

        to_remove = set()
        for word_x in self.domains[x]:
            # بررسی اینکه آیا word_x حداقل یک پشتیبان در domain[y] دارد یا نه
            has_support = False

            for word_y in self.domains[y]:
                if word_x[i] == word_y[j]:   # تطابق حرف مشترک
                    has_support = True
                    break

            if not has_support:
                to_remove.add(word_x)

        # حذف ها
        if to_remove:
            self.domains[x] -= to_remove
            revised = True

        return revised




    def pre_process_ac3(self):
        arcs = list()
        for x in self.domains:
            for y in self.crossword.neighbours(x):
                arcs.append((x, y))
        return arcs


    def ac3(self, arcs=None):
        """
        Enforce arc consistency using AC-3 algorithm.
        Return True if arc consistency is achieved without emptying a domain.
        Return False if some domain becomes empty.
        """

        # If no initial arcs are provided, initialize queue with all arcs
        if arcs is None:
            arcs = []
            for x in self.domains:
                for y in self.crossword.neighbours(x):
                    arcs.append((x, y))

        queue = list(arcs)

        while queue:
            x, y = queue.pop(0)

            # If revising x based on y removes values from domain[x]
            if self.revise(x, y):

                # If domain[x] becomes empty => contradiction => CSP unsolvable
                if len(self.domains[x]) == 0:
                    return False

                # Add all arcs (z, x) back to queue where z is a neighbor of x except y
                for z in self.crossword.neighbours(x):
                    if z != y:
                        queue.append((z, x))

        return True




    def is_assign_consistent(self, assignment):
        used = set()
        for v in assignment:
            if assignment[v] not in used:
                used.add(assignment[v])
            else:
                return False
            for n in self.crossword.neighbours(v):
                if n in assignment:
                    i, j = self.crossword.overlaps[v, n]
                    if assignment[v][i] != assignment[n][j]: return False
        return True

    def is_solved(self, assignment):
        '''
        Helper function to show whether the crossword is complete 
        '''
        return not bool(self.crossword.variables - set(assignment))
    

    def select_unassigned_var(self, assignment, heuristic):
        """
        Select an unassigned variable using:
        - MRV (minimum remaining values)
        - If heuristic=True, apply degree heuristic as a tiebreaker.
        """

        # متغیرهای بدون مقدار
        unassigned = [v for v in self.crossword.variables if v not in assignment]

        # 1) MRV: کمترین تعداد مقدار در دامنه
        # sort by size of domain
        unassigned.sort(key=lambda var: len(self.domains[var]))

        # گروه کمترین دامنه‌ها را پیدا می‌کنیم
        mrv_size = len(self.domains[unassigned[0]])
        mrv_candidates = [v for v in unassigned if len(self.domains[v]) == mrv_size]

        # اگر فقط یک کاندید MRV داریم → همان را برگردان
        if len(mrv_candidates) == 1 or not heuristic:
            return mrv_candidates[0]

        # 2) Degree Heuristic: بیشترین تعداد همسایه‌ی بدون مقدار
        # انتخاب متغیری که بیشترین محدودیت برای بقیه ایجاد می‌کند
        def degree(var):
            return sum(1 for n in self.crossword.neighbours(var) if n not in assignment)

        # بیشترین درجه = محدودیت بیشتر = بهتر برای انتخاب
        return max(mrv_candidates, key=degree)

    
    
    def order_domain_values(self, var, assignment):
        """
        Return domain values for `var` ordered by Least Constraining Value (LCV).
        LCV = value that rules out the fewest values in neighbors' domains.
        """

        # همسایه‌هایی که هنوز مقداردهی نشده‌اند
        neighbors = [
            n for n in self.crossword.neighbours(var)
            if n not in assignment
        ]

        def count_ruled_out(value):
            """
            Count how many values in neighbors' domains would be eliminated
            if `var` is assigned the word `value`.
            """
            eliminated = 0

            for n in neighbors:
                i, j = self.crossword.overlaps[var, n]
                for n_val in self.domains[n]:
                    if value[i] != n_val[j]:     # ناسازگار → حذف می‌شود
                        eliminated += 1

            return eliminated

        # مرتب‌سازی بر اساس کمترین مقدار حذف‌شده
        return sorted(self.domains[var], key=count_ruled_out)



    def backtrack(self, assignment):
        """
        Standard Backtracking Search with:
        - MRV
        - Degree heuristic
        - LCV
        - Consistency checking
        - Forward inference with AC-3
        """

        # اگر همه متغیرها مقداردهی شده‌اند → حل کامل شده
        if self.is_solved(assignment):
            return assignment

        # انتخاب متغیر با MRV / Degree
        var = self.select_unassigned_var(assignment, heuristic=self.heuristic)

        # ترتیب مقادیر براساس LCV
        ordered_values = self.order_domain_values(var, assignment)

        for value in ordered_values:

            # بررسی سازگاری مقدار با assignment موجود
            assignment[var] = value
            if self.is_assign_consistent(assignment):

                # ذخیره دامنه‌ها برای بازگردانی بعد از backtracking
                saved_domains = {v: self.domains[v].copy() for v in self.domains}

                # مقدار var را ثابت فرض کن
                self.domains[var] = {value}

                # AC-3 برای محدود کردن دامنه‌ها بعد از مقداردهی
                if self.ac3(self.pre_process_ac3()):

                    # ادامه backtracking
                    result = self.backtrack(assignment)
                    if result is not None:
                        return result

                # بازگردانی دامنه‌ها (undo)
                self.domains = saved_domains

            # اگر مقدار سازگار نبود → ارزش ندارد، حذفش می‌کنیم
            assignment.pop(var)

        # هیچ مقداری جواب نداد → شکست
        return None

    
    
    def solve(self):
        """Solve the crossword CSP by enforcing consistency and using backtracking search."""
        self.is_domain_consistent()
        arcs = self.pre_process_ac3()
        self.ac3(arcs)
        return self.backtrack(dict())
