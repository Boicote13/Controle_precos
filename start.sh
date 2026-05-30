#!/bin/bash

echo "Iniciando Django..."
python backend/manage.py runserver &
DJANGO_PID=$!

echo "Iniciando Streamlit..."
streamlit run precos_visual/visual.py &
STREAMLIT_PID=$!

echo ""
echo "=== Aplicações iniciadas ==="
echo "CRUD Django:  http://127.0.0.1:8000"
echo "Gráficos:     http://127.0.0.1:8501"
echo ""
echo "Pressione Enter para parar ambas..."

read -r

echo "Parando..."
kill $DJANGO_PID $STREAMLIT_PID 2>/dev/null
wait
echo "Aplicações encerradas."
