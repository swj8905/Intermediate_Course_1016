from sklearn.datasets import load_iris
import joblib
from sklearn.svm import SVC
import streamlit as st

iris= load_iris()
data = iris.data
label = iris.target

model = SVC()
model.fit(data, label)
# 모델 저장하기
joblib.dump(model, "model.pkl")

# 학습한 모델 불러오기
file = open("./model.pkl", "rb")
model = joblib.load(file)

# 제목
st.title("붓꽃 품종 예측")

# 사이드바 제목
st.sidebar.title("Features")
#Intializing
parameter_list=['Sepal length (cm)','Sepal Width (cm)','Petal length (cm)','Petal Width (cm)']
parameter_input_values=[]
parameter_default_values=['5.2','3.2','4.2','1.2']
values=[]

value1 = st.sidebar.slider(label="Sepal length (cm)", value=5.2, min_value=0.0, max_value=8.0)
value2 = st.sidebar.slider(label="Sepal width (cm)", value=3.2, min_value=0.0, max_value=8.0)
value3 = st.sidebar.slider(label="Petal length (cm)", value=4.2, min_value=0.0, max_value=8.0)
value4 = st.sidebar.slider(label="Petal width (cm)", value=1.2, min_value=0.0, max_value=8.0)

st.write('\n\n')


setosa= "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Kosaciec_szczecinkowaty_Iris_setosa.jpg/440px-Kosaciec_szczecinkowaty_Iris_setosa.jpg"
versicolor= "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Blue_Flag%2C_Ottawa.jpg/440px-Blue_Flag%2C_Ottawa.jpg"
virginica = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Iris_virginica_2.jpg/440px-Iris_virginica_2.jpg"
if st.button("Click Here to Classify"):
    prediction = model.predict([[value1, value2, value3, value4]])
    if prediction == 0:
        st.image(setosa)
        st.write("# Setosa")
    elif prediction == 1:
        st.image(versicolor)
        st.write("# Versicolor")
    elif prediction == 2:
        st.image(virginica)
        st.write("# virginica")
