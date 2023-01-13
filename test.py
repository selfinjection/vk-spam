import vk_captchasolver as vc

# captcha = vc.solve(sid=74838345480543) #Solve by sid and s
captcha = vc.solve(image='captcha.png') #Solve by sid only
print(captcha)