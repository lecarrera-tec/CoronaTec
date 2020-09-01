import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showerror
import os

#Establecer la ruta para ejecución relativa a la posición del archivo de intefaz, 
#por lo que los demás archivos deben estar junto a este
path = os.path.dirname(__file__)
os.chdir(path)
print(path)

#funcion para abrir Prueba de Preguntas Parametrizadas
def open_file_dir(widget, tipo_archivo, is_dir=False):
    #abrir cuadro de dialogo para solicitar archivo
    filepath = ""
    if is_dir:
        filepath = askdirectory()
    else:
        filepath = askopenfilename(
            filetypes=tipo_archivo
        )
    if not filepath:
        return 
    widget.configure(state='normal')
    widget.delete(0, tk.END)
    widget.insert(0, filepath)
    widget.configure(state='disabled')

#verifica que los archivos existan y llama a la aplicación generar.py
def call_generar():
    ppp_path = entry_file_ppp.get()
    student_list = entry_file_estudents.get()
    ind_rep = indice_repeticion.get()
    if not os.path.isfile(ppp_path):
        print(ppp_path)
        showerror(title="ERROR", message= "El archivo .ppp no existe")
        return
    if not (os.path.isfile(student_list) or os.path.isdir(student_list)):
        print(student_list)
        showerror(title="ERROR", message= "La ruta de la lista de estudiantes no es valida")
        return
    if(not str(ind_rep).isdigit):
        print(ind_rep)
        showerror(title="ERROR", message= "El indice de repetición debe ser un número")
        return
    command_line = 'python generar.py "' + ppp_path + '" "' + student_list + '" "' + str(ind_rep) + '"'
    print(command_line)
    os.system(command_line)

#verifica que los archivos existan y llama a la aplicación evaluar.py
def call_evaluar():
    ppp_path = entry_file_ppp.get()
    student_list = entry_file_estudents.get()
    ind_rep = indice_repeticion.get()
    resp_path = entry_file_respuestas.get()

    if not os.path.isfile(ppp_path):
        print(ppp_path)
        showerror(title="ERROR", message= "El archivo .ppp no existe")
        return
    if not (os.path.isfile(student_list) or os.path.isdir(student_list)):
        print(student_list)
        showerror(title="ERROR", message= "La ruta de la lista de estudiantes no es valida")
        return
    if(not str(ind_rep).isdigit):
        print(ind_rep)
        showerror(title="ERROR", message= "El indice de repetición debe ser un número")
        return
    if not os.path.isfile(resp_path):
        print(resp_path)
        showerror(title="ERROR", message= "El archivo .csv de respuestas no existe")
        return
    command_line = 'python evaluar.py "' + ppp_path + '" "' + student_list + '" "' + resp_path + '" "' + str(ind_rep) + '"'
    print(command_line)
    os.system(command_line)

#Ventana principal
window = tk.Tk()
window.title("Evaluaciones")
#################################################
#Primera funcion generar:
#- Requiere el archivo .ppp
#- La ruta de la lista (carpeta o archivo .csv)
#- Indice repeticion de examenes (opcional, precargar en 0)
#################################################

#Se empaca todo dentro de un frame
frame_generar = tk.Frame(master=window, borderwidth=1, padx = 10, pady = 10)
frame_generar.pack()

#Label indicar funcion generar:
#label_file_fun_generar = tk.Label(master=frame_generar, text="Generar")
#label_file_fun_generar.grid(column=0, row=0, columnspan = 3)

#Label para indicar archivo .ppp
label_file_ppp = tk.Label(master=frame_generar, text="1) Seleccionar archivo .ppp")
label_file_ppp.grid(column=0, row=1, columnspan = 3, sticky="w")
#campo de texto para mostrar la ruta seleccionada
entry_file_ppp = tk.Entry(master=frame_generar, width = 80)
entry_file_ppp.grid(column = 2, row = 2 , padx = 5, sticky="e")
#boton para abrir el archivo
button_open_file_ppp = tk.Button(master=frame_generar, text="Abrir .ppp", command = lambda: open_file_dir(entry_file_ppp,[("Prueba de Preguntas Parametrizadas .ppp", "*.ppp")]))
button_open_file_ppp.grid(column=1, row=2, padx = 5)

#Label para indicar lista o carpeta de estudiantes
label_file_estudents = tk.Label(master=frame_generar, text="2) Seleccionar lista de estudiantes (o directorio)")
label_file_estudents.grid(column=0, row=3, columnspan = 3, sticky="w")
#campo de texto para mostrar la ruta seleccionada
entry_file_estudents = tk.Entry(master=frame_generar, width = 80)
entry_file_estudents.grid(column = 2, row = 4 , padx = 5, sticky="e")
#boton para abrir el archivo
button_open_file_estudents = tk.Button(master=frame_generar, text="Lista estudiantes .csv", command = lambda: open_file_dir(entry_file_estudents,[("Lista de estudiantes .csv", "*.csv")]))
button_open_file_estudents.grid(column=0, row=4, padx = 5)
#boton para abrir el directorio
button_open_file_estudents = tk.Button(master=frame_generar, text="Directorio", command = lambda: open_file_dir(entry_file_estudents,[], True))
button_open_file_estudents.grid(column=1, row=4, padx = 5)

#Label para indicar indice de repeticion de examen
label_file_ind_rep = tk.Label(master=frame_generar, text="3) Índice de repetición de examen (opcional)")
label_file_ind_rep.grid(column=0, row=5, columnspan = 3, sticky="w")
#campo de texto para  indice de repeticion de examen
indice_repeticion = tk.IntVar()
indice_repeticion.set(0)
entry_file_ind_rep = tk.Entry(master=frame_generar, width = 6, textvariable=indice_repeticion)
entry_file_ind_rep.grid(column = 2, row = 6 , padx = 5, sticky="w")

#boton de generar
button_generar = tk.Button(master=frame_generar, text="Generar", command = call_generar )
button_generar.grid(column = 2, row = 7 , padx = 5, pady= 5, sticky="e")


#Label para indicar archivo .csv de las respuestas
label_file_respuestas = tk.Label(master=frame_generar, text="4) Seleccionar archivo .csv de las respuestas")
label_file_respuestas.grid(column=0, row=8, columnspan = 3, sticky="w")
#campo de texto para mostrar la ruta seleccionada
entry_file_respuestas = tk.Entry(master=frame_generar, width = 80)
entry_file_respuestas.grid(column = 2, row = 9 , padx = 5, sticky="e")
#boton de evaluar
button_evaluar = tk.Button(master=frame_generar, text="Evaluar", command = call_evaluar )
button_evaluar.grid(column = 2, row = 10 , padx = 5, pady= 5, sticky="e")

window.mainloop()