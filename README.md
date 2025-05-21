# Python_VM_with_Lark

이 프로젝트는 학습용으로 파이썬과 [Lark](https://github.com/lark-parser/lark)를 이용해 파이썬 스타일의 간단한 언어를 파싱하고, AST(추상 구문 트리) 생성, 바이트코드 생성, 그리고 바이트코드를 실행하는 가상머신(VM)까지 단계적으로 구현한 예제입니다.

## 주요 특징

- Lark로 문법 정의 및 파싱
- AST(추상 구문 트리) 변환
- 바이트코드 생성기(Code Generator)
- 바이트코드 실행 가상머신(Virtual Machine)
- 함수, 조건문, 반복문 등 점진적 기능 확장

## 폴더 구조

단계별 예제 코드 및 VM 구현
- ex1 : 변수, {+,-,*} 연산, print() 지원 포함
- ex2-1 : byterun VM 구조와 유사하게 Ex1코드를 refactoring
- ex2-2, ex2-3 : if 조건문, while 반복문 지원
- ex3-1 : 함수, Call stack 지원 포함
- ex3-2 : 최종 sample code, 문법 정의, VM

## 사용 예시

각 단계별 폴더에서 `pvm_with_lark.py`를 실행하면 샘플 코드의 파싱, AST, 바이트코드, 실행 결과를 확인할 수 있습니다.

---

학습 및 실습용으로 자유롭게 활용하세요!