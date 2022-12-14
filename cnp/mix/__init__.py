"""
Bottom-up approch:

1. async로 포팅하고자 하는 각 말단 함수들의 비동기 코루틴 버전을 새로 만든다.

2. 기존 동기 함수들을 변경시켜서 위에서 만든 코루틴 버전을 호출하고 임의의 실제 동작을 구현하는 대신 event loop에서 실행되도록 한다.

3. 상위 호출 hierarchy로 이동하여, 또다른 코루틴 계층을 작성하고, 기존 동기 함수 호출을 단계 1에서 정의한 코루틴 호출로 교체한다.

4. 단계 2에서 생성한 코루틴을 감싸는 동기 함수들은 더이상 필요치 않으므로 제거해서 연결부위들을 매끄럽게 한다.

"""