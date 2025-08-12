# Job Flow Diagram Guide

## 규칙

* 다이어그램의 첫 줄은 `master: [메인 객체 이름]`으로 시작한다.

 * 이 객체는 시스템 외부에 공개되는 유일한 진입점이다.
* 둘째 줄은 `Object: [객체 이름1, 객체 이름2, 객체 이름3, ...]`로 시작한다.

 * 메인 객체를 포함해 다이어그램에 등장하는 모든 객체를 나열한다.
* 객체 간의 협력과 의존 관계를 **이벤트**로 표현한다.
* 객체 내부 프로세스는 표시하지 않는 것을 권장한다.

 * 필요한 경우에 한해 동일 객체 내부의 `Public → Private` 한 단계 표기만 허용한다.
* 다이어그램 구성 요소

 * 다른 객체의 요청을 받아 처리하는 **Public 메서드**
 * 다른 객체의 도움이 필요할 때 발생시키는 **이벤트**
 * 메서드 호출의 **반환값**
* 마스터 객체의 Public 메서드가 시나리오의 시작점이 된다.

## 표현 규칙

### A가 B의 도움이 필요한 경우

```jobflow
A.OnEventName --> B.MethodName
```

* `OnEventName`은 이벤트를 의미한다.
* `MethodName`은 다른 객체로부터의 요청을 처리하는 Public 메서드를 의미한다.

### A가 B에게 데이터를 요청한 경우

```jobflow
A.OnEventName --> B.MethodName
B.MethodName.result --> A.MethodName
```

* 반환값은 메서드명 뒤에 점(`.`)을 붙여 `B.Method.result`처럼 표기한다.

### A가 B에게 데이터를 요청하고 결과를 C가 처리하는 경우

```jobflow
A.OnEventName --> B.MethodName
B.MethodName.result --> C.MethodName
```

### 반환 결과에 따라 분기해야 하는 경우 1

```jobflow
A.OnEventName --> B.MethodName
B.MethodName.Value1 --> C.MethodName
B.MethodName.Value2 --> D.MethodName
```

### 반환 결과에 따라 분기해야 하는 경우 2(불리언 분기)

```jobflow
A.OnEventName --> B.MethodName
B.MethodName.true --> C.HandleTrue
B.MethodName.false --> C.HandleFalse
```

### 반환 결과에 따라 분기해야 하는 경우 3(false는 무시)

```jobflow
A.OnEventName --> B.MethodName
B.MethodName.true --> C.MethodName
```

## 다이어그램 예제

```jobflow
master: VideoPlayer
Object: VideoPlayer, FileStream, VideoDecode, AudioDecode
VideoPlayer.Open --> VideoDecode.Init
VideoPlayer.Open --> AudioDecode.Init
VideoPlayer.Open --> FileStream.Open
VideoPlayer.Play --> FileStream.Start
FileStream.OnVideoData --> VideoDecode.Execute
FileStream.OnAudioData --> AudioDecode.Execute
```

* `VideoPlayer.Open`이 호출되면 `AudioDecode.Init`, `VideoDecode.Init`, `FileStream.Open`이 호출되어 동영상 재생을 준비한다.
* `VideoPlayer.Play`가 호출되면 `FileStream.Start`가 호출되어 동영상 재생을 시작한다.

 * `FileStream`의 내부 스레드가 동영상 데이터를 읽어 이벤트로 발생시킨다.
* `FileStream.OnVideoData`가 발생하면 `VideoDecode.Execute`가 호출되어 동영상 디코딩을 시작한다.
* `FileStream.OnAudioData`가 발생하면 `AudioDecode.Execute`가 호출되어 오디오 디코딩을 시작한다.
