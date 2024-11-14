#Interfaz principal
from tkinter import *
#Interfaz principal

root = Tk()
root.title("COMPILADOR MUSICAL - V1.0")
root.configure(bg='#1e1e1e')
root.state('zoomed')

# Configuración de colores
fg_color = '#d4d4d4'
bg_color = '#1e1e1e'
button_bg_color = '#3c3c3c'
button_fg_color = '#d4d4d4'
entry_bg_color = '#252526'
entry_fg_color = '#d4d4d4'

# Configuración de la disposición de filas y columnas
root.grid_rowconfigure(0, weight=15) #Fila 1 ocupa 1/4 del espacio
root.grid_rowconfigure(1, weight=85) #Fila 2 ocupa 3/4 del espacio
root.grid_columnconfigure(0, weight=1) #Columna 1 ocupa 1/1 del espacio

#Configuración del frame que contendrá los botones para ejecutar el codigo del compilador
frameButtons = Frame(root, bg='#1e1e1e')
frameButtons.grid(row = 0, column = 0, sticky = 'nsew')

#Configuración del frame que contendrá el editor de texto
frameText = Frame(root, bg='#1e1e1e')
frameText.grid(row = 1, column = 0, sticky = 'nsew')

#Configuracion de filas y columnas que tendrá el widget de texto
frameText.grid_rowconfigure(0, weight=100)
frameText.grid_columnconfigure(0, weight=25)
frameText.grid_columnconfigure(1, weight=75)

#Configuración de filas y columnas dentro de frameButtons
frameButtons.grid_rowconfigure(0, weight=100)
frameButtons.grid_columnconfigure(0, weight=50)
frameButtons.grid_columnconfigure(1, weight=50)



#Asignacion de botones en primera columna
btnAbrirArchivo = Button(frameButtons, text='Abrir archivo', bg=button_bg_color, fg=button_fg_color)
btnAbrirArchivo.grid(row=0, column=0)

btnCompilar = Button(frameButtons, text='Compilar', bg=button_bg_color, fg=button_fg_color)
btnCompilar.grid(row=0, column = 1)

#Colocamos el widget de texto para que el usuario escriba el código
code = Text(frameText, bg='#FFFFFF')
code.grid(row=0, column=1, sticky='nsew', padx=(0,20), pady=(0,20))

root.mainloop()