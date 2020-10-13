import sys

sys.setrecursionlimit(20000)
start = [-1, -1]
end = [-1, -1]
total_height = 160
total_width = 120
total_treshold = 50

def grayScale(sPic):
	bufPic = [];
	for i in range(total_height):
		for j in range(total_width):
			x = i * total_width + j
			p = sPic[x]
			r = (p & 0xff0000) >> 16	# взять значение компоненты красного
			g = (p & 0xff00) >> 8 # взять значение компоненты зеленого
			b = (p & 0xff) # взять значение компоненты синего
			p = r * 0.299 + g * 0.587 + b * 0.114 # компонента Y из YUV
			bufPic.append(p)
	return bufPic

# Бинаризация -- перевод изображения в ЧБ
def binarization(treshold, sPic):
	bufPic = []
	for i in range(len(sPic)):
		bufPic.append(255 if sPic[i] > treshold else 0);
	return bufPic;


def flat_to_matrix(img):
  mat = [[0] * total_height for i in range(total_width)]
  for i in range(total_width):
    for j in range(total_height):
      mat[i][j] = img[i * total_height + j]
  return mat
  
def matrix_to_flat(mat):
  output = []
  for i in range(total_width):
    for j in range(total_height):
      output.append(mat[i][j])
  return output

visited = [[0] * total_height for i in range(total_width)] 

def wave(mat, i, j, color):
  visited[i][j] = color
  if (i + 1 < total_width) and mat[i+1][j] == 0 and visited[i+1][j] == 0:
    wave(mat, i+1, j, color)
  if (j + 1 < total_height) and mat[i][j+1] == 0 and visited[i][j+1] == 0:
    wave(mat, i, j + 1, color)
  if (i - 1 >= 0) and mat[i-1][j] == 0 and visited[i-1][j] == 0:
    wave(mat, i-1, j, color)
  if (j - 1 >= 0) and mat[i][j-1] == 0 and visited[i][j-1] == 0:
    wave(mat, i, j - 1, color)

def start_wave(mat):
  color = 1
  for i in range(total_width):
    for j in range(total_height):
      if visited[i][j] == 0 and mat[i][j] == 0:
        wave(mat, i, j, color)
        color += 1
  m = {}
  for i in range(total_width):
    for j in range(total_height):
      try:
        m[visited[i][j]] += 1
      except:
        m[visited[i][j]] = 0
        
  color, count = 0, 0      
  for i in m:
    if i != 0 and m[i] > count:
      color = i
      count = m[i]
  find_vertices(color)


def find_vertices(color):
  global start, end
  for i in range(total_height):
    for j in range(total_width):
      if visited[j][i] == color and start == [-1, -1]:
        start = [j, i]
      elif visited[j][i] == color:
        end = [j, i]

# взять кадр в формате rgb32
pic = getPhoto();
brick.display().show(pic, total_height, total_width, "rgb32");
#script.wait(2000);

pic = grayScale(pic)
pic = binarization(total_treshold, pic)

Mat = flat_to_matrix(pic)
start_wave(Mat)
ff = matrix_to_flat(Mat)

ans = [[-1] * 5 for i in range(5)] 
s_x, s_y = start
e_x, e_y = end
print(s_x, s_y)
print(e_x, e_y)
print()
if(s_y < e_y):
  dx = e_x - s_x
  ddx = round(dx / 5)
  dy = e_y - s_y
  ddy = round(dy / 5)
  tg_a = dy / dx
  print(tg_a)
  for i in range(5):
    for j in range(5):
      print((s_x + i * ddx + ddx//2), (s_y + j * ddy + ddy//2))
      ans[i][j] = Mat[(s_x + i * ddx + ddx//2)][(s_y + j * ddy + ddy//2)]
print(ans)
  
  

brick.display().show(ff, total_height, total_width, "grayscale8")


script.wait(10000)

