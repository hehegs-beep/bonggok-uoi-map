"""Select concise, activity-specific original guidance; retain source and reasons.

The topic vocabulary represents editorial choices, not Google/official code
assignments. Candidates are restricted to the same official area. Generic
teaching/evaluation language cannot earn a match. Explicit source assignments
take priority. Unmatched standards deliberately have no displayed notes.
"""
import json
import re
from pathlib import Path
from build_upper_guidance import BOOKS, build_book, CODE

ROOT=Path(__file__).resolve().parents[1]
TOPICS={
 '국': '''감정|감정을|기분
 공감|인물의마음|인물의처지
 말차례|차례를지키|교대
 집중하여듣|경청|집중해서듣
 대화|대화를
 예의|예절|높임|호칭|인사
 발표|청중|목소리|말소리
 준언어|억양|어조|강세
 비언어|표정|시선|몸동작|몸짓
 토의|학급회의|원탁회의
 토론|찬반|반론
 면담|면담자
 이유|근거|뒷받침
 타당|비판적
 요약|간추리|중심내용|중심생각|중요한내용
 질문|의문
 예측|추론|생략|함축
 사실과의견|의견을구분
 출처|신뢰|믿을만
 읽기습관|읽기효능감|읽기에대한자신감|읽기에흥미|읽기동기
 정확하게읽|정확한발음|정확성
 유창|띄어읽|의미단위
 글자|자모|한글|소릿값
 문장|문장성분|호응
 문단|중심문장|뒷받침문장
 글쓰기과정|쓰기과정|고쳐쓰|고쳐쓴|통일성
 생각이나느낌|생각과느낌|꾸며주는말
 설명하는글|설명글|설명문|대상의특성
 주장하는글|주장글|논설문
 겪은일|체험한일|일기
 쓰기에흥미|쓰기흥미|쓰기에적극|독자와공유
 단어|국어사전|낱말
 표준어|방언
 고유어|관용표현
 시간표현|시제
 띄어쓰기|맞춤법|표기
 의성어|의태어|말놀이|말의재미
 낭송|시나노래|동시|시의
 비유|비유적
 이야기|소설|서사
 작가|창작의도
 갈래|시와소설|시와이야기
 경험과상상|사실과허구|허구
 성찰|자신의삶
 매체이용|매체생활|이용습관
 복합양식|매체자료제작|매체자료를제작
 인터넷|탐색|검색
 음성언어|문자언어
 저작권|인용''',
 '수': '''수세기|수를세|세어보
 자릿값|위치적기수법
 큰수|다섯자리|10000
 수의크기|크기를비교|수의계열
 수의분해|분해하고|합성
 덧셈|더하기
 뺄셈|빼기
 곱셈|곱하는|곱셈구구
 나눗셈|나누는|나누어떨어|몫과나머지|검산
 어림|양감
 분수|분모|분자|등분할
 소수|소수점
 약수|배수
 최대공약수|최소공배수
 혼합계산|계산순서
 등호|등식|동치
 규칙|규칙성
 대응관계|대응하는
 비의|비로|비율|백분율
 비례식|비례배분
 원기둥|원뿔|구의모양|구의구성
 직육면체|정육면체
 각기둥|각뿔
 전개도
 쌓기나무|입체도형의위|입체도형의앞
 삼각형|이등변|정삼각형
 사각형|정사각형|직사각형|평행사변형|마름모|사다리꼴
 다각형|정다각형|대각선
 (?<!단)원의|반지름|지름|원주율
 선분|직선|반직선
 평행|수직
 각도|직각|예각|둔각|분도기
 평면도형의이동|밀기|뒤집기|돌리기
 점의이동|위치와방향|격자
 합동|대칭|대응점|대응변|대응각
 길이|센티미터|(?<![A-Za-z])cm(?![²³23])|밀리미터|킬로미터
 시각|시계|시간|초단위
 들이|리터|mL
 무게|그램|kg
 넓이|제곱센티미터|제곱미터
 부피|세제곱|겉넓이
 표로|표를|분류
 그래프|그림그래프|막대그래프|꺾은선그래프|띠그래프|원그래프
 평균
 가능성|확률''',
 '도': '''감정|자기존중|자신을존중
 정직
 성실|시간관리
 관점|도덕규범
 자주|주체적|주도적
 반성|성찰|생활습관|자기생활
 진로|직업|적성을|적성에
 효의|효,|효와|효를|효행|우애|가족
 친구|우정|배려
 공감|도덕적상상력
 봉사|이타심
 편견|다양성|차이존중
 인공지능|로봇
 공정|정의
 인권|권리
 통일|북한
 세계시민|인류애|다른나라
 자연|생명|생태|동식물
 지속가능|미래세대''',
 '사': '''장소감|장소의경험|장소에서의경험
 살기좋은|좋은점|불편한점|편익
 시간의흐름|시간개념|시간감각|시간적위치|시간표현
 오래된|증거|유물|사료
 역사자료|문헌|사진|영상|증언
 지역의변화|달라진생활|변화와지속
 사회변화|저출산|고령화|정보화
 다양한문화|다문화|문화적편견
 지형|지리적환경|자연환경
 교통|통신|이동수단
 지도|방위|기호|축척|등고선
 지역문제|지역의문제|주민참여
 국가유산|문화유산
 민주주의|민주화
 선거|투표|주권
 국회|행정부|법원|권력분립
 미디어|가짜뉴스
 희소성|선택|합리적소비
 생산|소비|경제활동
 교류|상호의존
 인구|인구분포|인구밀도|인구구조
 도시|촌락
 역사적인물|역사적사건|역사적사실
 조선|고려|삼국|고조선
 일제|독립|광복
 대한민국정부|정부수립
 분단|평화통일|통일
 산업화|경제성장
 인권|기본권|헌법
 (?<!방)법의|(?<!방)법과|법을|법이
 지구본|위도|경도|세계지도
 대륙|대양|영토|국가의위치
 기후|기온|강수
 가계|기업|근로자
 무역|국가간거래
 지구촌문제|지구촌의평화|난민|국제기구|비정부기구
 지속가능|기후변화|생태계파괴''',
 '과': '''무게|무거운|가벼운|저울
 힘의|힘을|밀거나당|지레
 동물|곤충
 식물|잎의|잎을
 분류|기준을세워
 한살이|성장과정
 생명과학|균류|세균|원생생물
 서식|환경에적응
 육지|바다|대기
 소리|떨림|진동
 질병|감염|예방접종
 자석|자기력|극의
 물의상태|얼음|수증기|응결|증발
 강주변|흐르는물|침식|퇴적
 화산|지진
 달의|달을|별자리|행성|밤하늘
 생태계|먹이|생물요소|비생물
 기체|공기의|공기를
 기후변화|탄소
 지층|화석
 빛의|빛을|직진|반사|굴절|프리즘
 용해|용질|용매|용액|진하기
 뼈|근육|기관|호흡|소화|순환|배설
 혼합물|분리|거름|증류
 날씨|기상|이슬|안개|구름|비와눈
 온도|온도계|열의|열을|전도|대류
 자원|에너지|재생
 산성|염기성|지시약|리트머스
 물체의운동|속력|위치의변화|좌표
 세포|현미경
 식물의구조|뿌리|줄기|광합성|증산
 지구의자전|지구의공전|낮과밤
 태양고도|남중고도|계절변화|계절의변화
 (?<!자)연소|불꽃|소화기|소화방법
 전기회로|전지|전구|직렬|병렬
 전자석
 전기안전|전기를안전|효율적으로
 진로|직업''',
 '실': '''발달|아동기|사춘기
 가족|돌봄|배려
 가정일|일의가치
 진로|직업|적성|흥미와성격
 식사|영양|식재료|음식|밥상|조리
 옷|의생활|의복
 생활용품|바느질|수선
 생활자원|재활용|재사용
 시간관리|시간과용돈|용돈|소비
 생태|지속가능|환경을고려
 발명|특허|발명사고
 수송|운송
 구조물|건설
 동식물|농업|농촌|재배|사육
 로봇|융합기술
 컴퓨터|디지털기기
 알고리즘|프로그래밍|프로그램|코딩
 데이터|아날로그
 인공지능|기계학습''',
 '체': '''체력|체력운동|체력수준
 건강습관|건강한생활|생활습관
 성장발달|사춘기
 이동움직임|걷기|달리기|점프
 비이동|제자리|구부리기|비틀기
 조작움직임|던지기|공차기|라켓
 복합움직임|연결한움직임
 기술형|동작형|기록형|투기형
 전략형|영역형|필드형|네트형
 생태형|자연환경형|생활환경형
 인내|목표달성|경기결과
 협력|팀원|역할|의사결정
 배려|상대존중|스포츠퍼슨십
 스포츠환경|환경보호|생태적감수성
 움직임요소|신체요소|노력요소|공간요소|관계요소
 모방|흉내
 추상|느낌과생각
 리듬|박자
 도구|소도구
 스포츠표현|창작체조|음악줄넘기
 전통표현|민속무용
 현대표현|자유로운|창작무용
 감상|아름다움|심미''',
 '음': '''자세|주법|발성
 음악요소|음악의요소
 가락|리듬|박자|장단(?!점)
 신체표현|놀이
 생활속|음악생활|생활화
 악곡의특징|음악적특징|비교
 분위기|쓰임|배경
 국악|음악문화유산|전통음악
 느낌|상상|즉흥
 악보|기보|표기
 바꾸어|바꾸기|변형
 조건|음악만들|음악을만들
 매체|디지털
 연계|융합
 저작권''',
 '미': '''감각|촉각|시각|청각
 자신과대상|자신을탐색
 주변환경|생활속미술
 이미지|시각문화|광고
 관찰|상상|아이디어
 재료|용구|도구|표현재료
 조형요소|색의|색을|(?<!개)선의|형태
 조형원리|균형|비례|강조
 디지털|매체
 표현과정|성찰|작품을발전
 융합|타교과
 작품의특징|내용과형식|내용과형식
 시대적|지역적|배경
 질문|미술가
 감상관점|서로다른관점|다양한방법
 미술문화|공동체|전시|문화유산''',
 '영': '''알파벳|대소문자
 소리와철자|파닉스|음소|해독
 강세|리듬|억양
 단어|어구
 주요정보|구체적정보|명시적정보
 줄거리|중심내용|주제
 순서|세부정보
 전략|추측|예측
 시나노래|시,노래|이야기|문학
 문화|존중|다양성
 매체|디지털|에듀테크
 흥미|자신감
 인사|소개|감사|사과
 감정|의견|경험|계획
 질문|답하기|대화
 철자|구두점|문장부호
 글쓰기과정|쓰기과정|고쳐쓰|수정
 그림|도표|실물|동작''',
 '통합': '''학교적응|학교생활|학교안팎|학교의
 안전|건강
 나를|자신을|자아|자기이해
 가족|친척|이웃
 배려|공감|소통
 생태|동식물|자연|생명
 공동체|마을|지역
 우리나라|나라사랑
 다른나라|여러나라|다문화
 다양성|차이|다양한생각
 호기심|도전|새로운활동
 상상|창의|새롭게
 하루|시간|규칙적
 계절|날씨|절기
 과거|현재|미래|인물
 지속가능|재활용|환경보호
 아동권리|아동의권리|인권|안녕
 주제|관심있는|조사
 매체|디지털
 성찰|되돌아|학습을돌아
 놀이|놀잇감
 신체|움직임|운동
 문화예술|축제|공연|전시
 협력|여럿|함께''',
}

def compact(t):return re.sub(r'\s+','',t)
PATTERNS={k:[re.compile(line.strip()) for line in v.splitlines() if line.strip()] for k,v in TOPICS.items()}

def topic_matches(subject, statement, note):
 target=compact(statement);candidate=compact(note)
 if '용어와기호' in candidate:return []
 if re.search(r'성취기준이주로|이영역의모든|영역내모든|성취기준의내용은|표현에서평가는',candidate):return []
 hits=[p.pattern for p in PATTERNS[subject] if p.search(target) and p.search(candidate)]
 # A curriculum progression reference alone is not a classroom consideration.
 if re.search(r'연계된다\.?$',note) and re.search(r'중학교|학년군',note):return []
 # Do not use a reading-only activity for a listening-only English standard, or vice versa.
 if subject=='영':
  if '듣' in target and '읽' not in target and '읽' in candidate and '듣' not in candidate:return []
  if '읽' in target and '듣' not in target and '듣' in candidate and '읽' not in candidate:return []
  if re.search(r'전략|추측|예측',candidate) and not re.search(r'전략|추측|예측',target):return []
 if subject=='수':
  if '분수' in target and '소수' in candidate and '분수' not in candidate:return []
  if '소수' in target and '분수' in candidate and '소수' not in candidate:return []
  if '부피' in target and '넓이' in candidate and '부피' not in candidate:return []
  if '넓이' in target and '부피' in candidate and '넓이' not in candidate:return []
  if '단위' in target and not re.search(r'단위|측정|눈금',candidate):return []
  operations=['나눗셈','곱셈','덧셈','뺄셈']
  target_ops=[op for op in operations if op in target]
  if target_ops and not any(op in candidate for op in target_ops):return []
  if not target_ops and any(op in candidate for op in operations):return []
 if subject=='과' and '직렬' not in target and '직렬' in candidate and '비교' in candidate:return []
 if candidate.count('능력')>=3 and '평가' in candidate:return []
 return hits

def main():
 path=ROOT/'curriculum-data.js'
 payload=json.loads(path.read_text(encoding='utf-8').split('window.CURRICULUM_GUIDANCE = ',1)[1].rstrip().removesuffix(';'))
 original={'sources':{},'groups':{},'entries':{}}
 for n,(subject,drive) in {**BOOKS,15:('통합','1mrFIrfAtlohsvP1i90h-s7_O4VARRZaY')}.items():
  build_book(n,subject,drive,original,include_lower=True)
 audit=[]
 for code,entry in payload['entries'].items():
  raw=original['entries'].get(code)
  if raw is None:raise ValueError('Missing original curriculum: '+code)
  subject=re.match(r'\d+([가-힣]+)',code)[1]
  if subject in ('바','슬','즐'):subject='통합'
  group=original['groups'][raw['group']]
  # Keep the complete original and existing notes in the internal data.
  entry['displayExplanation']=raw['explanation']
  entry['originalStatement']=raw['statement']
  candidates=[]
  for i,note in enumerate(raw['notes']):
   candidates.append((100, i,{**note,'selection':{'kind':'explicit-code','codes':[code]}}))
  for i,note in enumerate(group['commonItems']):
   hits=topic_matches(subject,raw['statement'],note['text'])
   if hits:
    # Narrow, repeated subject matter outranks a single broad activity match.
    score=len(hits)*3
    if len(hits)==1 and hits[0] in ('대화|대화를','문장|문장성분|호응','단어|국어사전|낱말','단어|어구','흥미|자신감','그림|도표|실물|동작','주제|관심있는|조사','놀이|놀잇감','안전|건강','느낌|상상|즉흥','매체|디지털','디지털|매체','생활속|음악생활|생활화','신체|움직임|운동','감상|아름다움|심미'):
     continue
    candidates.append((score,100+i,{**note,'selection':{'kind':'activity-match','topics':hits,'sourceGroup':raw['group']}}))
  chosen=[];seen=set()
  for score,i,note in sorted(candidates,key=lambda x:(-x[0],x[1])):
   text=compact(note['text'])
   if text in seen:continue
   chosen.append(note);seen.add(text)
   if len(chosen)==3:break
  entry['displayNotes']=chosen
  entry['displaySource']={'fileId':original['sources'][group['source']]['fileId'],'group':raw['group'],'notice':'교육부 고시 제2022-33호'}
  audit.append({'code':code,'statement':raw['statement'],'notes':[{'text':n['text'],'selection':n['selection']} for n in chosen]})
 payload['version']='2026-10-16-focused'
 path.write_text('/* Original text, focused editorial note selections, and retained provenance. */\nwindow.CURRICULUM_GUIDANCE = '+json.dumps(payload,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
 (ROOT/'tmp/focused-guidance-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Focused:',len(audit),'standards;',sum(bool(e['displayExplanation'])for e in payload['entries'].values()),'original explanations;',sum(len(e['displayNotes'])for e in payload['entries'].values()),'selected notes')

if __name__=='__main__':main()
